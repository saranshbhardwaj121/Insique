import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

from backend.app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    logger.warning("hash_password called: type=%s, len=%d, repr=%r",
                   type(password).__name__, len(password), password[:20])
    try:
        result = pwd_context.hash(password)
        logger.warning("hash_password succeeded: hash starts with %r", result[:10])
        return result
    except Exception as exc:
        logger.exception("hash_password FAILED: %s: %s", type(exc).__name__, exc)
        raise


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.refresh_token_expire_days)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "type": "refresh",
        "jti": uuid4().hex,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc


def get_token_expiration(payload: dict[str, Any]) -> datetime:
    exp = payload.get("exp")
    if isinstance(exp, int | float):
        return datetime.fromtimestamp(exp, tz=timezone.utc)
    if isinstance(exp, datetime):
        return exp
    raise ValueError("Invalid token expiration")
