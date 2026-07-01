import logging

import httpx

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    settings = get_settings()
    api_key = settings.resend_api_key
    from_email = settings.from_email

    if not api_key or not from_email:
        logger.info(
            "Password reset email not sent: RESEND_API_KEY or FROM_EMAIL not configured. "
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
                "subject": "Reset your Insique password",
                "html": f"""
                    <p>You requested a password reset for your Insique account.</p>
                    <p>Click the link below to reset your password. This link expires in 15 minutes.</p>
                    <p><a href="{reset_url}">{reset_url}</a></p>
                    <p>If you did not request this, please ignore this email.</p>
                """,
            },
            timeout=30,
        )
        response.raise_for_status()
        logger.info("Password reset email sent to %s", to_email)
        return True
    except httpx.HTTPError as exc:
        logger.error("Failed to send password reset email to %s: %s", to_email, exc)
        return False
