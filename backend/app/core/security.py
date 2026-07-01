import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import bcrypt
import jwt

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    try:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    except Exception as exc:
        logger.exception("hash_password failed")
        raise


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


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


def create_password_reset_token(subject: str, expires_minutes: int = 15) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "purpose": "password_reset",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.InvalidTokenError as exc:
        raise ValueError("Invalid token") from exc


def get_token_expiration(payload: dict[str, Any]) -> datetime:
    exp = payload.get("exp")
    if isinstance(exp, int | float):
        return datetime.fromtimestamp(exp, tz=timezone.utc)
    if isinstance(exp, datetime):
        return exp
    raise ValueError("Invalid token expiration")
