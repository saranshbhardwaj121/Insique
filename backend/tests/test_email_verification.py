"""Tests for email verification flow."""
import hashlib
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from backend.app.api.deps import get_session
from backend.app.core.config import get_settings
from backend.app.main import app
from backend.app.models.base import Base
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.services.verification_service import (
    _hash_token,
    _generate_verification_token,
    create_verification_token,
    verify_email,
    resend_verification,
    VerificationError,
    VERIFICATION_TOKEN_EXPIRE_HOURS,
    RESEND_COOLDOWN_MINUTES,
)
from backend.app.services.email_service import send_verification_email

settings = get_settings()
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def prepare_schema() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM oauth_sessions"))
        conn.execute(text("DELETE FROM refresh_tokens WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'vrfy_%')"))
        conn.execute(text("DELETE FROM users WHERE username LIKE 'vrfy_%'"))


@pytest.fixture()
def db_session() -> Session:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.execute(text("DELETE FROM oauth_sessions"))
        db.execute(text("DELETE FROM refresh_tokens WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'vrfy_%')"))
        db.execute(text("DELETE FROM users WHERE username LIKE 'vrfy_%'"))
        db.commit()
        db.close()


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def override_get_session() -> Session:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _create_unverified_user(db_session: Session, email: str | None = None) -> User:
    uid = uuid4().hex[:8]
    user = User(
        username=f"vrfy_{uid}",
        email=email or f"vrfy_{uid}@example.com",
        password_hash="dummy",
        email_verified=False,
    )
    db_session.add(user)
    db_session.commit()
    return user


def _create_verified_user(db_session: Session) -> User:
    uid = uuid4().hex[:8]
    user = User(
        username=f"vrfy_{uid}",
        email=f"vrfy_{uid}@example.com",
        password_hash="dummy",
        email_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


def _create_google_user(db_session: Session) -> User:
    uid = uuid4().hex[:8]
    user = User(
        username=f"vrfy_{uid}",
        email=f"vrfy_{uid}@example.com",
        password_hash="dummy",
        email_verified=True,
        auth_provider="GOOGLE",
    )
    db_session.add(user)
    db_session.commit()
    return user


def _register_user(client: TestClient) -> dict:
    uid = uuid4().hex[:8]
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": f"vrfy_{uid}",
            "email": f"vrfy_{uid}@example.com",
            "password": "TestPass123",
        },
    )
    return resp.json()


# ---------------------------------------------------------------------------
# Tests: Registration
# ---------------------------------------------------------------------------

class TestRegistrationSendsVerification:
    def test_verification_email_sent(self, client: TestClient) -> None:
        uid = uuid4().hex[:8]
        with patch("backend.app.services.auth_service.send_password_reset_email") as mock_pwd, \
             patch("backend.app.services.verification_service.send_verification_email") as mock_verify:
            mock_verify.return_value = True
            resp = client.post(
                "/api/v1/auth/register",
                json={
                    "username": f"vrfy_{uid}",
                    "email": f"vrfy_{uid}@example.com",
                    "password": "TestPass123",
                },
            )
        assert resp.status_code == 201
        assert mock_verify.called
        assert not resp.json()["email_verified"]

    def test_hashed_token_stored(self, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        token = create_verification_token(user)
        db_session.commit()

        assert user.verification_token_hash is not None
        assert user.verification_token_hash == _hash_token(token)
        assert user.verification_token_hash != token

    def test_expiry_stored(self, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        before = datetime.now(timezone.utc)
        token = create_verification_token(user)
        db_session.commit()
        after = datetime.now(timezone.utc)

        assert user.verification_token_expires_at is not None
        expected = before + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
        assert user.verification_token_expires_at >= expected - timedelta(seconds=1)
        assert user.verification_token_expires_at <= after + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS) + timedelta(seconds=1)


# ---------------------------------------------------------------------------
# Tests: Verification
# ---------------------------------------------------------------------------

class TestVerification:
    def test_valid_token(self, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        token = create_verification_token(user)
        db_session.commit()

        result = verify_email(token, db_session)
        assert result.email_verified is True
        assert result.verification_token_hash is None
        assert result.verification_token_expires_at is None

    def test_expired_token(self, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        token = create_verification_token(user)
        user.verification_token_expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        db_session.commit()

        with pytest.raises(VerificationError, match="expired"):
            verify_email(token, db_session)

    def test_invalid_token(self, db_session: Session) -> None:
        with pytest.raises(VerificationError, match="Invalid"):
            verify_email("nonexistent_token", db_session)

    def test_already_verified(self, db_session: Session) -> None:
        user = _create_verified_user(db_session)
        token = create_verification_token(user)
        db_session.commit()

        with pytest.raises(VerificationError, match="already verified"):
            verify_email(token, db_session)

    def test_token_cannot_be_reused(self, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        token = create_verification_token(user)
        db_session.commit()

        verify_email(token, db_session)

        with pytest.raises(VerificationError, match="Invalid"):
            verify_email(token, db_session)

    def test_verify_email_endpoint_success(self, client: TestClient, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        token = create_verification_token(user)
        db_session.commit()

        resp = client.get(f"/api/v1/auth/verify-email?token={token}")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Email verified successfully"

    def test_verify_email_endpoint_expired(self, client: TestClient, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        token = create_verification_token(user)
        user.verification_token_expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        db_session.commit()

        resp = client.get(f"/api/v1/auth/verify-email?token={token}")
        assert resp.status_code == 400
        assert "expired" in resp.json()["detail"].lower()

    def test_verify_email_endpoint_invalid(self, client: TestClient) -> None:
        resp = client.get("/api/v1/auth/verify-email?token=invalidtoken")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Tests: Resend verification
# ---------------------------------------------------------------------------

class TestResendVerification:
    def test_new_token_generated(self, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        token1 = create_verification_token(user)
        user.verification_sent_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        db_session.commit()
        old_hash = user.verification_token_hash

        with patch("backend.app.services.verification_service.send_verification_email") as mock:
            mock.return_value = True
            resend_verification(user, db_session)

        assert user.verification_token_hash is not None
        assert user.verification_token_hash != old_hash

    def test_old_token_invalidated(self, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        token1 = create_verification_token(user)
        user.verification_sent_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        db_session.commit()

        with patch("backend.app.services.verification_service.send_verification_email") as mock:
            mock.return_value = True
            resend_verification(user, db_session)

        with pytest.raises(VerificationError, match="Invalid"):
            verify_email(token1, db_session)

    def test_cooldown_enforced(self, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        user.verification_sent_at = datetime.now(timezone.utc)
        user.verification_token_hash = "oldhash"
        db_session.commit()

        with pytest.raises(VerificationError, match="wait"):
            resend_verification(user, db_session)

    def test_resend_endpoint_unauthenticated(self, client: TestClient) -> None:
        resp = client.post("/api/v1/auth/resend-verification")
        assert resp.status_code == 401

    def test_resend_endpoint_success(self, client: TestClient, db_session: Session) -> None:
        uid = uuid4().hex[:8]
        with patch("backend.app.services.verification_service.send_verification_email") as mock_reg:
            mock_reg.return_value = True
            resp = client.post(
                "/api/v1/auth/register",
                json={
                    "username": f"vrfy_{uid}",
                    "email": f"vrfy_{uid}@example.com",
                    "password": "TestPass123",
                },
            )
        assert resp.status_code == 201

        # Move verification_sent_at back to bypass cooldown
        user = db_session.query(User).filter_by(username=f"vrfy_{uid}").first()
        assert user is not None
        user.verification_sent_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        db_session.commit()

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"identifier": f"vrfy_{uid}", "password": "TestPass123"},
        )
        assert login_resp.status_code == 200
        tokens = login_resp.json()
        access_token = tokens["access_token"]

        with patch("backend.app.services.verification_service.send_verification_email") as mock:
            mock.return_value = True
            resp2 = client.post(
                "/api/v1/auth/resend-verification",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        assert resp2.status_code == 200
        assert resp2.json()["message"] == "Verification email sent"

    def test_resend_refuses_google_user(self, db_session: Session) -> None:
        user = _create_google_user(db_session)
        with pytest.raises(VerificationError, match="automatically verified"):
            resend_verification(user, db_session)

    def test_resend_refuses_already_verified(self, db_session: Session) -> None:
        user = _create_verified_user(db_session)
        with pytest.raises(VerificationError, match="already verified"):
            resend_verification(user, db_session)


# ---------------------------------------------------------------------------
# Tests: Security
# ---------------------------------------------------------------------------

class TestSecurity:
    def test_plaintext_token_not_stored(self, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        token = create_verification_token(user)
        db_session.commit()

        assert user.verification_token_hash != token
        assert user.verification_token_hash == hashlib.sha256(token.encode()).hexdigest()

    def test_hash_lookup_works(self, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        token = create_verification_token(user)
        db_session.commit()

        from backend.app.repositories.user_repository import UserRepository
        repo = UserRepository(db_session)
        found = repo.get_by_verification_token_hash(_hash_token(token))
        assert found is not None
        assert found.id == user.id

    def test_expiry_enforced(self, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        token = create_verification_token(user)
        user.verification_token_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db_session.commit()

        with pytest.raises(VerificationError, match="expired"):
            verify_email(token, db_session)


# ---------------------------------------------------------------------------
# Tests: Middleware / verified user requirement
# ---------------------------------------------------------------------------

class TestVerifiedUserMiddleware:
    def test_verified_user_succeeds(self, client: TestClient, db_session: Session) -> None:
        user = _create_verified_user(db_session)
        from backend.app.core.security import create_access_token
        token = create_access_token(subject=str(user.id))

        resp = client.post(
            "/api/v1/watchlists",
            json={"name": "Test Watchlist"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code != 403

    def test_unverified_user_blocked(self, client: TestClient, db_session: Session) -> None:
        user = _create_unverified_user(db_session)
        from backend.app.core.security import create_access_token
        token = create_access_token(subject=str(user.id))

        resp = client.post(
            "/api/v1/watchlists",
            json={"name": "Test Watchlist"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
        assert "verify" in resp.json()["detail"].lower()

    def test_google_user_bypasses_verification(self, client: TestClient, db_session: Session) -> None:
        user = _create_google_user(db_session)
        from backend.app.core.security import create_access_token
        token = create_access_token(subject=str(user.id))

        resp = client.post(
            "/api/v1/watchlists",
            json={"name": "Test Watchlist"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code != 403


# ---------------------------------------------------------------------------
# Tests: Regression — existing auth flows unchanged
# ---------------------------------------------------------------------------

class TestRegressionAuthUnchanged:
    def test_password_login_unchanged(self, client: TestClient) -> None:
        uid = uuid4().hex[:8]
        client.post(
            "/api/v1/auth/register",
            json={
                "username": f"vrfy_{uid}",
                "email": f"vrfy_{uid}@example.com",
                "password": "TestPass123",
            },
        )
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"identifier": f"vrfy_{uid}", "password": "TestPass123"},
        )
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

    def test_refresh_unchanged(self, client: TestClient) -> None:
        uid = uuid4().hex[:8]
        client.post(
            "/api/v1/auth/register",
            json={
                "username": f"vrfy_{uid}",
                "email": f"vrfy_{uid}@example.com",
                "password": "TestPass123",
            },
        )
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"identifier": f"vrfy_{uid}", "password": "TestPass123"},
        )
        tokens = login_resp.json()
        refresh_resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh_resp.status_code == 200

    def test_reset_password_unchanged(self, client: TestClient) -> None:
        uid = uuid4().hex[:8]
        email = f"vrfy_{uid}@example.com"
        client.post(
            "/api/v1/auth/register",
            json={
                "username": f"vrfy_{uid}",
                "email": email,
                "password": "TestPass123",
            },
        )
        forgot_resp = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": email},
        )
        assert forgot_resp.status_code == 200

    def test_me_endpoint_works(self, client: TestClient, db_session: Session) -> None:
        uid = uuid4().hex[:8]
        client.post(
            "/api/v1/auth/register",
            json={
                "username": f"vrfy_{uid}",
                "email": f"vrfy_{uid}@example.com",
                "password": "TestPass123",
            },
        )
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"identifier": f"vrfy_{uid}", "password": "TestPass123"},
        )
        tokens = login_resp.json()
        me_resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["email_verified"] is False
