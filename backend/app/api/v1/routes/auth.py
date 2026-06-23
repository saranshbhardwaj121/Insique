import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from backend.app.api.deps import get_current_user, get_session
from backend.app.core.config import get_settings
from backend.app.models.user import User
from backend.app.schemas.auth import (
    AuthTokensResponse,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterRequest,
)
from backend.app.schemas.user import UserRead
from backend.app.services.auth_service import AuthService
from backend.app.services.rate_limit_service import LoginRateLimiter

router = APIRouter()
settings = get_settings()
login_rate_limiter = LoginRateLimiter(
    max_attempts=settings.login_rate_limit_attempts,
    window_seconds=settings.login_rate_limit_window_seconds,
)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: Session = Depends(get_session)) -> UserRead:
    logger.warning("POST /register: username=%r, email=%r, password_type=%s, password_len=%d, password_repr=%r",
                   payload.username, payload.email,
                   type(payload.password).__name__, len(payload.password), payload.password[:20])
    service = AuthService(session)
    try:
        user = service.register_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
        )
        return UserRead.model_validate(user)
    except ValueError as exc:
        logger.exception("POST /register FAILED: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=AuthTokensResponse)
def login(
    payload: LoginRequest,
    request: Request,
    session: Session = Depends(get_session),
) -> AuthTokensResponse:
    rate_limit_key = f"{request.client.host}:{payload.identifier.lower()}" if request.client else payload.identifier.lower()
    if not login_rate_limiter.is_allowed(rate_limit_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )

    service = AuthService(session)
    user = service.authenticate_user(identifier=payload.identifier, password=payload.password)
    if user is None:
        login_rate_limiter.register_failure(rate_limit_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    login_rate_limiter.reset(rate_limit_key)

    access_token = service.issue_access_token(user)
    refresh_token = service.issue_refresh_token(user)
    return AuthTokensResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AuthTokensResponse)
def refresh(
    payload: RefreshTokenRequest,
    session: Session = Depends(get_session),
) -> AuthTokensResponse:
    service = AuthService(session)
    try:
        user = service.user_from_refresh_token(payload.refresh_token)
        service.revoke_refresh_token(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    access_token = service.issue_access_token(user)
    refresh_token = service.issue_refresh_token(user)
    return AuthTokensResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, session: Session = Depends(get_session)) -> None:
    service = AuthService(session)
    try:
        service.revoke_refresh_token(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
