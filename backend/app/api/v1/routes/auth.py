import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from backend.app.api.deps import get_current_user, get_session
from backend.app.core.config import get_settings
from backend.app.models.user import User
from backend.app.schemas.auth import (
    AuthTokensResponse,
    DeleteAccountRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    PasswordResetResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
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
forgot_password_rate_limiter = LoginRateLimiter(
    max_attempts=settings.forgot_password_rate_limit_attempts,
    window_seconds=settings.forgot_password_rate_limit_window_minutes * 60,
)
register_rate_limiter = LoginRateLimiter(
    max_attempts=3,
    window_seconds=3600,
)
reset_password_rate_limiter = LoginRateLimiter(
    max_attempts=5,
    window_seconds=900,
)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, session: Session = Depends(get_session)) -> UserRead:
    rate_limit_key = f"register:{request.client.host}" if request.client else payload.email
    if not register_rate_limiter.is_allowed(rate_limit_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Try again later.",
        )

    service = AuthService(session)
    try:
        user = service.register_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
        )
        register_rate_limiter.reset(rate_limit_key)
        return UserRead.model_validate(user)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create account. Please check your details and try again.",
        )


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
            detail="Invalid or expired refresh token",
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
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/forgot-password", response_model=PasswordResetResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    session: Session = Depends(get_session),
) -> PasswordResetResponse:
    rate_limit_key = f"forgot_pwd:{request.client.host}" if request.client else payload.email
    if not forgot_password_rate_limiter.is_allowed(rate_limit_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again later.",
        )

    forgot_password_rate_limiter.register_failure(rate_limit_key)
    service = AuthService(session)
    service.send_password_reset_email(payload.email)
    return PasswordResetResponse(
        message="If an account exists, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    session: Session = Depends(get_session),
) -> PasswordResetResponse:
    rate_limit_key = f"reset_pwd:{request.client.host}" if request.client else "global"
    if not reset_password_rate_limiter.is_allowed(rate_limit_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset attempts. Try again later.",
        )

    service = AuthService(session)
    try:
        user_id = service.verify_password_reset_token(payload.token)
        service.reset_password(user_id, payload.password)
    except (ValueError, Exception):
        reset_password_rate_limiter.register_failure(rate_limit_key)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )

    return PasswordResetResponse(message="Password has been reset successfully.")


@router.delete("/delete-account", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    payload: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    service = AuthService(session)
    try:
        service.delete_account(current_user.id, payload.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to delete account. Please check your password.",
        )


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
