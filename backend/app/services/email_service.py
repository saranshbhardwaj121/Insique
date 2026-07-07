import logging

import httpx

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


def _send_email(to_email: str, subject: str, html: str) -> bool:
    settings = get_settings()
    api_key = settings.resend_api_key
    from_email = settings.from_email

    if not api_key or not from_email:
        logger.info(
            "Email not sent: RESEND_API_KEY or FROM_EMAIL not configured. "
            "Would send to %s",
            to_email,
        )
        return False

    try:
        response = httpx.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html,
            },
            timeout=30,
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc)
        return False


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    html = f"""
        <p>You requested a password reset for your Insique account.</p>
        <p>Click the link below to reset your password. This link expires in 15 minutes.</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>If you did not request this, please ignore this email.</p>
    """
    sent = _send_email(to_email, "Reset your Insique password", html)
    if sent:
        logger.info("Password reset email sent to %s", to_email)
    return sent


def send_verification_email(to_email: str, verify_url: str) -> bool:
    html = f"""
        <h2>Welcome to Insique!</h2>
        <p>Thanks for creating an account. Please verify your email address to get started.</p>
        <p style="margin: 24px 0;">
            <a href="{verify_url}" style="background-color:#2563eb;color:white;padding:12px 24px;border-radius:6px;text-decoration:none;display:inline-block;">
                Verify Email
            </a>
        </p>
        <p>Or copy this link into your browser:</p>
        <p><a href="{verify_url}">{verify_url}</a></p>
        <p>This link expires in 24 hours.</p>
        <p>If you did not create an account, please ignore this email.</p>
    """
    sent = _send_email(to_email, "Verify your Insique email", html)
    if sent:
        logger.info("Verification email sent to %s", to_email)
    return sent
