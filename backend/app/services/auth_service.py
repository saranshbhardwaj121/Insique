import logging
import secrets
import time
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from backend.app.core.config import get_settings
from backend.app.core.security import (
    create_access_token,
    create_password_reset_token,
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
from backend.app.services.email_service import send_password_reset_email


class AuthService:
    MAX_FAILED_ATTEMPTS = 10
    LOCKOUT_DURATION_MINUTES = 15

    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)

    def register_user(self, username: str, email: str, password: str) -> User:
        email = email.lower().strip()
        username = username.strip()

        existing_username = self.users.get_by_username(username)
        if existing_username is not None:
            raise ValueError("Username already exists")

        existing_email = self.users.get_by_email(email)
        if existing_email is not None:
            raise ValueError("Email already exists")

        user = User(username=username, email=email, password_hash=hash_password(password))
        self.session.add(user)
        try:
            self.session.commit()
            self.session.refresh(user)
        except Exception:
            self.session.rollback()
            raise
        return user

    def authenticate_user(self, identifier: str, password: str) -> User | None:
        identifier = identifier.lower().strip()
        user = self.users.get_by_username(identifier) or self.users.get_by_email(identifier)
        if user is None:
            return None

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            return None

        if not verify_password(password, user.password_hash):
            self.users.increment_failed_attempts(user.id)
            self.session.commit()
            return None

        self.users.reset_failed_attempts(user.id)
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

    def create_password_reset_token(self, user_id: UUID) -> str:
        settings = get_settings()
        return create_password_reset_token(
            subject=str(user_id),
            expires_minutes=settings.password_reset_expire_minutes,
        )

    def verify_password_reset_token(self, token: str) -> UUID:
        payload = decode_token(token)
        purpose = payload.get("purpose")
        subject = payload.get("sub")
        if purpose != "password_reset" or subject is None:
            raise ValueError("Invalid or expired password reset token")
        return UUID(subject)

    def reset_password(self, user_id: UUID, new_password: str) -> None:
        user = self.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise ValueError("User not found")
        user.password_hash = hash_password(new_password)
        if user.auth_provider == "GOOGLE":
            user.auth_provider = "BOTH"
        revoked = self.refresh_tokens.revoke_all_by_user_id(user_id)
        if revoked:
            logger.info("Revoked %d refresh tokens for user %s", revoked, user_id)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def send_password_reset_email(self, email: str) -> bool:
        user = self.users.get_by_email(email)
        if user is None or not user.is_active:
            time.sleep(secrets.randbelow(300) / 1000 + 0.2)
            return True
        token = self.create_password_reset_token(user.id)
        settings = get_settings()
        reset_url = f"{settings.frontend_url}/reset-password/{token}"
        return send_password_reset_email(to_email=email, reset_url=reset_url)

    def delete_account(self, user_id: UUID, password: str) -> None:
        user = self.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise ValueError("User not found")
        if user.auth_provider == "GOOGLE":
            pass
        elif not verify_password(password, user.password_hash):
            raise ValueError("Invalid password")
        revoked = self.refresh_tokens.revoke_all_by_user_id(user_id)
        if revoked:
            logger.info("Revoked %d refresh tokens for user %s", revoked, user_id)
        try:
            self.users.delete_by_id(user_id)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        if not isinstance(jti, str):
            raise ValueError("Invalid refresh token")

        revoked = self.refresh_tokens.revoke_by_jti(jti)
        if revoked:
            self.session.commit()
        return revoked
