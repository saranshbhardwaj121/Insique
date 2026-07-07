import logging
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

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
from backend.app.schemas.user import UserRead, VerificationResponse, ResendVerificationResponse
from backend.app.services.auth_service import AuthService
from backend.app.services.verification_service import send_verification, verify_email, resend_verification, VerificationError
from backend.app.services.google_auth_service import (
    GoogleAuthError,
    GoogleAuthService,
    create_google_authorization_url,
    generate_oauth_state,
    encode_oauth_state_cookie,
    decode_oauth_state_cookie,
    STATE_COOKIE_NAME,
    STATE_COOKIE_MAX_AGE,
)
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
google_callback_rate_limiter = LoginRateLimiter(
    max_attempts=20,
    window_seconds=60,
)


@router.get("/google/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
def google_login() -> RedirectResponse:
    """Redirect the user to Google's OAuth consent screen with CSRF state."""
    try:
        state = generate_oauth_state()
        signed = encode_oauth_state_cookie(state, settings)
        url = create_google_authorization_url(state=state)
        redirect = RedirectResponse(url=url)
        redirect.set_cookie(
            key=STATE_COOKIE_NAME,
            value=signed,
            max_age=STATE_COOKIE_MAX_AGE,
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax",
            path="/api/v1/auth/google",
        )
        return redirect
    except GoogleAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )


@router.get("/google/callback")
def google_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    request: Request = None,
    session: Session = Depends(get_session),
):
    """Handle the Google OAuth callback.

    Validates state for CSRF protection, exchanges the authorization code,
    creates a one-time session code, and redirects to the frontend.
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google OAuth error: {error}",
        )
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code",
        )

    # Validate state for CSRF protection
    state_cookie = request.cookies.get(STATE_COOKIE_NAME) if request else None
    if state_cookie:
        expected_state = decode_oauth_state_cookie(state_cookie, settings)
        if expected_state is None or expected_state != state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OAuth state. Possible CSRF attack.",
            )

    google_svc = GoogleAuthService(session)
    auth_svc = AuthService(session)

    try:
        user = google_svc.handle_google_callback(code)
    except GoogleAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

    session_code = google_svc.create_session_code(user)
    access_token = auth_svc.issue_access_token(user)
    refresh_token = auth_svc.issue_refresh_token(user)

    frontend_url = settings.frontend_url.rstrip("/")
    logger.info("Frontend redirect URL: %s", frontend_url)
    params = urlencode({"code": session_code})
    redirect = RedirectResponse(url=f"{frontend_url}/auth/google/callback?{params}")
    redirect.delete_cookie(
        key=STATE_COOKIE_NAME,
        path="/api/v1/auth/google",
    )
    return redirect


@router.post("/google/exchange", response_model=AuthTokensResponse)
def google_exchange(
    payload: dict,
    request: Request,
    session: Session = Depends(get_session),
) -> AuthTokensResponse:
    """Exchange a one-time session code for full auth tokens."""
    rate_limit_key = f"google_exchange:{request.client.host}" if request.client else "global"
    if not google_callback_rate_limiter.is_allowed(rate_limit_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again later.",
        )

    code = payload.get("code")
    if not code or not isinstance(code, str):
        google_callback_rate_limiter.register_failure(rate_limit_key)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing session code",
        )

    google_svc = GoogleAuthService(session)
    auth_svc = AuthService(session)

    try:
        user = google_svc.exchange_session_code(code)
    except GoogleAuthError as exc:
        google_callback_rate_limiter.register_failure(rate_limit_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

    access_token = auth_svc.issue_access_token(user)
    refresh_token = auth_svc.issue_refresh_token(user)
    google_callback_rate_limiter.reset(rate_limit_key)
    return AuthTokensResponse(access_token=access_token, refresh_token=refresh_token)


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
        send_verification(user, session)
        register_rate_limiter.reset(rate_limit_key)
        return UserRead.model_validate(user)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create account. Please check your details and try again.",
        )


@router.get("/verify-email", response_model=VerificationResponse)
def verify_email_endpoint(
    token: str,
    session: Session = Depends(get_session),
) -> VerificationResponse:
    try:
        verify_email(token, session)
        logger.info("Email verification succeeded for token")
        return VerificationResponse(message="Email verified successfully")
    except VerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post("/resend-verification", response_model=ResendVerificationResponse)
def resend_verification_endpoint(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ResendVerificationResponse:
    try:
        resend_verification(current_user, session)
        logger.info("Verification email resent to user %s", current_user.email)
        return ResendVerificationResponse(message="Verification email sent")
    except VerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
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
