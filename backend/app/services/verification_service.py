import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.services.email_service import send_verification_email

logger = logging.getLogger(__name__)

VERIFICATION_TOKEN_EXPIRE_HOURS = 24
RESEND_COOLDOWN_MINUTES = 5


class VerificationError(Exception):
    pass


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _generate_verification_token() -> str:
    return secrets.token_urlsafe(32)


def create_verification_token(user: User) -> str:
    token = _generate_verification_token()
    token_hash = _hash_token(token)
    user.verification_token_hash = token_hash
    user.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
    user.verification_sent_at = datetime.now(timezone.utc)
    return token


def send_verification(user: User, session: Session) -> None:
    settings = get_settings()
    token = create_verification_token(user)
    session.commit()

    verify_url = f"{settings.frontend_url.rstrip('/')}/auth/verify-email?token={token}"
    sent = send_verification_email(to_email=user.email, verify_url=verify_url)
    if sent:
        logger.info("Verification email sent to %s", user.email)
    else:
        logger.warning("Verification email not sent to %s (Resend API not configured)", user.email)


def verify_email(token: str, session: Session) -> User:
    token_hash = _hash_token(token)
    users_repo = UserRepository(session)
    user = users_repo.get_by_verification_token_hash(token_hash)
    if user is None:
        logger.warning("Verification failed: invalid token hash")
        raise VerificationError("Invalid verification link")

    if user.email_verified:
        logger.info("Verification skipped: user %s already verified", user.email)
        raise VerificationError("Email already verified")

    if user.verification_token_expires_at is None or user.verification_token_expires_at < datetime.now(timezone.utc):
        logger.warning("Verification failed: token expired for user %s", user.email)
        raise VerificationError("Verification link has expired")

    user.email_verified = True
    user.verification_token_hash = None
    user.verification_token_expires_at = None
    session.commit()

    logger.info("Email verified successfully for user %s", user.email)
    return user


def resend_verification(user: User, session: Session) -> None:
    if user.auth_provider == "GOOGLE":
        raise VerificationError("Google accounts are automatically verified")

    if user.email_verified:
        raise VerificationError("Email already verified")

    if user.verification_sent_at and (datetime.now(timezone.utc) - user.verification_sent_at) < timedelta(minutes=RESEND_COOLDOWN_MINUTES):
        raise VerificationError("Please wait before requesting another verification email")

    user.verification_token_hash = None
    user.verification_token_expires_at = None
    send_verification(user, session)
    logger.info("Verification email resent to %s", user.email)
