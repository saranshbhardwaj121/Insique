import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from backend.app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_expiration,
    hash_password,
    verify_password,
)
from backend.app.models.refresh_token import RefreshToken
from backend.app.models.user import User
from backend.app.repositories.refresh_token_repository import RefreshTokenRepository
from backend.app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)

    def register_user(self, username: str, email: str, password: str) -> User:
        logger.warning("register_user: username=%r, email=%r, password type=%s, password len=%d, password repr=%r",
                       username, email, type(password).__name__, len(password), password[:20])
        existing_username = self.users.get_by_username(username)
        if existing_username is not None:
            raise ValueError("Username already exists")

        existing_email = self.users.get_by_email(email)
        if existing_email is not None:
            raise ValueError("Email already exists")

        user = User(username=username, email=email, password_hash=hash_password(password))
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def authenticate_user(self, identifier: str, password: str) -> User | None:
        user = self.users.get_by_username(identifier) or self.users.get_by_email(identifier)
        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        user.last_login_at = datetime.now(timezone.utc)
        self.session.commit()
        return user

    def issue_access_token(self, user: User) -> str:
        return create_access_token(subject=str(user.id))

    def issue_refresh_token(self, user: User) -> str:
        token = create_refresh_token(subject=str(user.id))
        payload = decode_token(token)
        jti = payload.get("jti")
        if not isinstance(jti, str):
            raise ValueError("Invalid refresh token payload")

        db_token = RefreshToken(
            user_id=user.id,
            token_jti=jti,
            expires_at=get_token_expiration(payload),
        )
        self.refresh_tokens.create(db_token)
        self.session.commit()
        return token

    def user_from_refresh_token(self, refresh_token: str) -> User:
        payload = decode_token(refresh_token)
        token_type = payload.get("type")
        subject = payload.get("sub")
        jti = payload.get("jti")
        if token_type != "refresh" or subject is None or not isinstance(jti, str):
            raise ValueError("Invalid refresh token")

        active_token = self.refresh_tokens.get_active_by_jti(jti)
        if active_token is None:
            raise ValueError("Refresh token is revoked or expired")

        user = self.users.get_by_id(UUID(subject))
        if user is None or not user.is_active:
            raise ValueError("Invalid refresh token")
        return user

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        if not isinstance(jti, str):
            raise ValueError("Invalid refresh token")

        revoked = self.refresh_tokens.revoke_by_jti(jti)
        if revoked:
            self.session.commit()
        return revoked
