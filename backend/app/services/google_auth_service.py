import logging
import secrets
import string
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode
from uuid import uuid4

import httpx
import jwt
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models.oauth_session import OAuthSession
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

GOOGLE_ISSUERS = {"https://accounts.google.com", "accounts.google.com"}
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v1/certs"

SESSION_CODE_EXPIRE_MINUTES = 5
STATE_COOKIE_NAME = "oauth_state"
STATE_COOKIE_MAX_AGE = 600


class GoogleAuthError(RuntimeError):
    pass


@dataclass
class GoogleUserInfo:
    google_id: str
    email: str
    name: str
    picture: str | None
    email_verified: bool


def _generate_unique_username(suggested: str, users: UserRepository) -> str:
    candidate = suggested[:50]
    existing = users.get_by_username(candidate)
    if existing is None:
        return candidate
    for i in range(2, 100):
        candidate = f"{suggested[:45]}{i}"[:50]
        if users.get_by_username(candidate) is None:
            return candidate
    suffix = secrets.token_hex(4)
    return f"{suggested[:45]}_{suffix}"[:50]


def _derive_username_from_email(email: str) -> str:
    local = email.split("@")[0].lower()
    safe = "".join(c for c in local if c.isalnum() or c in "._-")
    safe = safe[:50]
    if not safe:
        safe = "user"
    return safe


def create_google_authorization_url(state: str | None = None, settings: Any = None) -> str:
    if settings is None:
        settings = get_settings()
    if not settings.google_client_id or not settings.google_redirect_uri:
        raise GoogleAuthError("Google OAuth is not configured")

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    if state:
        params["state"] = state
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


def _exchange_code_for_tokens(code: str, settings: Any) -> dict[str, Any]:
    try:
        resp = httpx.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        raise GoogleAuthError("Failed to exchange authorization code") from exc
    except httpx.RequestError as exc:
        raise GoogleAuthError("Network error during token exchange") from exc


def _verify_google_id_token(id_token: str, settings: Any) -> dict[str, Any]:
    try:
        header = jwt.get_unverified_header(id_token)
    except jwt.DecodeError as exc:
        raise GoogleAuthError("Invalid ID token format") from exc

    unverified = jwt.decode(id_token, options={"verify_signature": False})

    iss = unverified.get("iss")
    if iss not in GOOGLE_ISSUERS:
        raise GoogleAuthError(f"Invalid token issuer: {iss}")

    aud = unverified.get("aud")
    if aud != settings.google_client_id:
        raise GoogleAuthError(f"Invalid token audience: {aud}")

    try:
        resp = httpx.get(GOOGLE_CERTS_URL, timeout=15)
        resp.raise_for_status()
        certs = resp.json()
    except httpx.RequestError as exc:
        raise GoogleAuthError("Failed to fetch Google public keys") from exc

    kid = header.get("kid", "")
    public_key = certs.get(kid)
    if public_key is None:
        raise GoogleAuthError("Matching public key not found")

    try:
        payload = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=settings.google_client_id,
            issuer=iss,
        )
    except jwt.ExpiredSignatureError as exc:
        raise GoogleAuthError("ID token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise GoogleAuthError("Invalid ID token") from exc

    if not payload.get("email_verified", False):
        raise GoogleAuthError("Google email is not verified")

    return payload


def extract_google_user_info(id_token_payload: dict[str, Any]) -> GoogleUserInfo:
    return GoogleUserInfo(
        google_id=str(id_token_payload["sub"]),
        email=id_token_payload["email"].lower().strip(),
        name=id_token_payload.get("name", ""),
        picture=id_token_payload.get("picture"),
        email_verified=bool(id_token_payload.get("email_verified", False)),
    )


def generate_oauth_state() -> str:
    return secrets.token_urlsafe(32)


def decode_oauth_state_cookie(cookie_value: str, settings: Any) -> str | None:
    try:
        payload = jwt.decode(cookie_value, settings.secret_key, algorithms=[settings.jwt_algorithm])
        state = payload.get("state")
        if isinstance(state, str):
            return state
    except jwt.InvalidTokenError:
        pass
    return None


def encode_oauth_state_cookie(state: str, settings: Any) -> str:
    payload = {
        "state": state,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=STATE_COOKIE_MAX_AGE),
        "purpose": "oauth_state",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


class GoogleAuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.settings = get_settings()

    def handle_google_callback(self, code: str) -> User:
        tokens = _exchange_code_for_tokens(code, self.settings)
        id_token = tokens.get("id_token")
        if not id_token:
            raise GoogleAuthError("No ID token in provider response")

        payload = _verify_google_id_token(id_token, self.settings)
        google_user = extract_google_user_info(payload)

        user = self._find_or_create_user(google_user)
        user.last_login_at = datetime.now(timezone.utc)
        self.session.commit()
        return user

    def _find_or_create_user(self, google_user: GoogleUserInfo) -> User:
        existing = self.users.get_by_google_id(google_user.google_id)
        if existing is not None:
            return existing

        existing_email = self.users.get_by_email(google_user.email)
        if existing_email is not None:
            existing_email.google_id = google_user.google_id
            existing_email.auth_provider = "GOOGLE"
            existing_email.avatar_url = google_user.picture
            existing_email.email_verified = google_user.email_verified
            return existing_email

        username = _derive_username_from_email(google_user.email)
        safe_username = _generate_unique_username(username, self.users)

        user = User(
            username=safe_username,
            email=google_user.email,
            password_hash=secrets.token_hex(32),
            google_id=google_user.google_id,
            auth_provider="GOOGLE",
            avatar_url=google_user.picture,
            email_verified=google_user.email_verified,
            is_active=True,
        )
        self.session.add(user)
        self.session.flush()
        return user

    def create_session_code(self, user: User) -> str:
        code = secrets.token_urlsafe(48)
        session_code = OAuthSession(
            code=code,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=SESSION_CODE_EXPIRE_MINUTES),
        )
        self.session.add(session_code)
        self.session.commit()
        return code

    def exchange_session_code(self, code: str) -> User:
        session_code = (
            self.session.query(OAuthSession)
            .filter(
                OAuthSession.code == code,
                OAuthSession.used == False,
                OAuthSession.expires_at > datetime.now(timezone.utc),
            )
            .with_for_update()
            .first()
        )
        if session_code is None:
            raise GoogleAuthError("Invalid or expired session code")

        session_code.used = True
        self.session.commit()

        user = self.users.get_by_id(session_code.user_id)
        if user is None or not user.is_active:
            raise GoogleAuthError("User not found")
        return user
