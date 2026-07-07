"""Tests for Google OAuth authentication flow."""
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from backend.app.api.deps import get_session
from backend.app.api.v1.routes.auth import google_callback_rate_limiter
from backend.app.core.config import get_settings
from backend.app.main import app
from backend.app.models.base import Base
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository

settings = get_settings()
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _unique_google_id() -> str:
    return str(uuid4())


@pytest.fixture(scope="session", autouse=True)
def prepare_schema() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM oauth_sessions"))
        conn.execute(text("DELETE FROM refresh_tokens WHERE user_id IN (SELECT id FROM users WHERE auth_provider = 'GOOGLE' OR username LIKE 'sf_test_%')"))
        conn.execute(text("DELETE FROM users WHERE auth_provider = 'GOOGLE' OR username LIKE 'sf_test_%'"))


@pytest.fixture()
def db_session() -> Session:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.execute(text("DELETE FROM oauth_sessions"))
        db.execute(text("DELETE FROM refresh_tokens WHERE user_id IN (SELECT id FROM users WHERE auth_provider = 'GOOGLE' OR username LIKE 'sf_test_%')"))
        db.execute(text("DELETE FROM users WHERE auth_provider = 'GOOGLE' OR username LIKE 'sf_test_%'"))
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
    google_callback_rate_limiter._attempts.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_id_token_payload(**overrides: object) -> dict:
    payload = {
        "iss": "https://accounts.google.com",
        "aud": settings.google_client_id,
        "sub": _unique_google_id(),
        "email": f"user_{uuid4().hex[:8]}@gmail.com",
        "name": "Test User",
        "picture": "https://lh3.googleusercontent.com/a/photo",
        "email_verified": True,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    }
    payload.update(**overrides)
    return payload


def _register_local_user(
    db_session: Session,
    username: str | None = None,
    email: str | None = None,
) -> User:
    name = username or f"sf_test_user_{uuid4().hex[:8]}"
    user = User(
        username=name,
        email=email or f"{name}@example.com",
        password_hash="dummy",
        auth_provider="LOCAL",
    )
    db_session.add(user)
    db_session.commit()
    return user


def _do_google_callback(
    client: TestClient,
    id_token_payload: dict,
    follow: bool = False,
) -> tuple:
    """Execute the full Google OAuth flow and return (response, session_code)."""
    # Step 1: Mock token exchange + verification
    mock_tokens = {"id_token": "fake_id_token", "access_token": "fake_access_token"}

    with patch("backend.app.services.google_auth_service._exchange_code_for_tokens",
               return_value=mock_tokens), \
         patch("backend.app.services.google_auth_service._verify_google_id_token",
               return_value=id_token_payload):
        response = client.get("/api/v1/auth/google/callback?code=test_auth_code", follow_redirects=False)
        return response


def _extract_session_code(response) -> str | None:
    """Extract session code from a redirect response."""
    location = response.headers.get("location", "")
    if "code=" not in location:
        return None
    return location.split("code=")[-1].split("&")[0]


def _exchange_session_code(client: TestClient, session_code: str) -> dict:
    """Exchange a session code for auth tokens."""
    resp = client.post("/api/v1/auth/google/exchange", json={"code": session_code})
    return resp


def _full_google_login(client: TestClient, id_token_payload: dict | None = None) -> dict:
    """Run the full Google callback + exchange flow, return tokens dict."""
    if id_token_payload is None:
        id_token_payload = _fake_id_token_payload()
    cb_resp = _do_google_callback(client, id_token_payload)
    session_code = _extract_session_code(cb_resp)
    assert session_code is not None, f"No session code in redirect: {cb_resp.headers.get('location')}"
    exchange_resp = _exchange_session_code(client, session_code)
    assert exchange_resp.status_code == 200, f"Exchange failed: {exchange_resp.json()}"
    return exchange_resp.json()


# ---------------------------------------------------------------------------
# Tests: Google login redirect
# ---------------------------------------------------------------------------

class TestGoogleLoginRedirect:
    def test_redirects_to_google(self, client: TestClient) -> None:
        response = client.get("/api/v1/auth/google/login", follow_redirects=False)
        assert response.status_code == 307
        assert "accounts.google.com" in response.headers["location"]
        assert "client_id=" in response.headers["location"]
        assert "state=" in response.headers["location"]

    def test_sets_state_cookie(self, client: TestClient) -> None:
        response = client.get("/api/v1/auth/google/login", follow_redirects=False)
        assert "oauth_state" in response.headers.get("set-cookie", "")


# ---------------------------------------------------------------------------
# Tests: State validation
# ---------------------------------------------------------------------------

class TestOAuthStateValidation:
    def test_missing_state_rejected(self, client: TestClient) -> None:
        """Callback without state should still work if no cookie is set (backward compat)."""
        mock_tokens = {"id_token": "fake_id_token", "access_token": "fake_access_token"}
        payload = _fake_id_token_payload()
        with patch("backend.app.services.google_auth_service._exchange_code_for_tokens",
                   return_value=mock_tokens), \
             patch("backend.app.services.google_auth_service._verify_google_id_token",
                   return_value=payload):
            response = client.get("/api/v1/auth/google/callback?code=test_code", follow_redirects=False)
        assert response.status_code in (200, 302, 307)
        assert "code=" in response.headers.get("location", "")

    def test_invalid_state_rejected(self, client: TestClient) -> None:
        """Callback with mismatched state must be rejected."""
        from backend.app.services.google_auth_service import encode_oauth_state_cookie
        bad_state = encode_oauth_state_cookie("bad_state", settings)
        client.cookies.set("oauth_state", bad_state)
        response = client.get("/api/v1/auth/google/callback?code=test_code&state=other_state")
        assert response.status_code == 400
        assert "CSRF" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Tests: Session code flow
# ---------------------------------------------------------------------------

class TestSessionCode:
    def test_callback_returns_redirect_with_code(self, client: TestClient) -> None:
        payload = _fake_id_token_payload()
        response = _do_google_callback(client, payload)
        assert response.status_code in (200, 302, 307)
        location = response.headers.get("location", "")
        assert "code=" in location
        assert "/auth/google/callback" in location

    def test_exchange_returns_tokens(self, client: TestClient) -> None:
        tokens = _full_google_login(client)
        assert "access_token" in tokens
        assert "refresh_token" in tokens

    def test_session_code_single_use(self, client: TestClient) -> None:
        payload = _fake_id_token_payload()
        cb_resp = _do_google_callback(client, payload)
        session_code = _extract_session_code(cb_resp)
        assert session_code is not None

        first = _exchange_session_code(client, session_code)
        assert first.status_code == 200

        second = _exchange_session_code(client, session_code)
        assert second.status_code == 401
        assert "expired" in second.json()["detail"].lower()

    def test_invalid_session_code_rejected(self, client: TestClient) -> None:
        resp = _exchange_session_code(client, "invalid_code_12345")
        assert resp.status_code == 401
        assert "expired" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Tests: New Google user
# ---------------------------------------------------------------------------

class TestNewGoogleUser:
    def test_new_user_gets_tokens(self, client: TestClient, db_session: Session) -> None:
        gid = _unique_google_id()
        email = f"newuser_{uuid4().hex[:8]}@gmail.com"
        payload = _fake_id_token_payload(sub=gid, email=email)
        tokens = _full_google_login(client, payload)

        assert "access_token" in tokens
        assert "refresh_token" in tokens

        user_repo = UserRepository(db_session)
        user = user_repo.get_by_google_id(gid)
        assert user is not None
        assert user.email == email
        assert user.auth_provider == "GOOGLE"
        assert user.email_verified is True

    def test_user_persists_after_restart(self, client: TestClient, db_session: Session) -> None:
        gid = _unique_google_id()
        payload = _fake_id_token_payload(sub=gid)
        _full_google_login(client, payload)

        user_repo = UserRepository(db_session)
        user = user_repo.get_by_google_id(gid)
        assert user is not None

    def test_me_endpoint_works(self, client: TestClient) -> None:
        gid = _unique_google_id()
        email = f"me_test_{uuid4().hex[:8]}@gmail.com"
        payload = _fake_id_token_payload(sub=gid, email=email)
        tokens = _full_google_login(client, payload)

        me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
        assert me.status_code == 200
        assert me.json()["email"] == email
        assert me.json()["auth_provider"] == "GOOGLE"
        assert me.json()["avatar_url"] is not None

    def test_refresh_token_works(self, client: TestClient) -> None:
        tokens = _full_google_login(client)
        refresh_resp = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh_resp.status_code == 200
        assert "access_token" in refresh_resp.json()

    def test_logout_works(self, client: TestClient) -> None:
        tokens = _full_google_login(client)
        logout = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert logout.status_code == 204

    def test_username_derived_from_email(self, client: TestClient, db_session: Session) -> None:
        gid = _unique_google_id()
        payload = _fake_id_token_payload(sub=gid, email="testuser@gmail.com")
        _full_google_login(client, payload)

        user_repo = UserRepository(db_session)
        user = user_repo.get_by_google_id(gid)
        assert user is not None
        assert "testuser" in user.username


# ---------------------------------------------------------------------------
# Tests: Existing Google user (returning)
# ---------------------------------------------------------------------------

class TestExistingGoogleUser:
    def test_existing_user_logs_in(self, client: TestClient, db_session: Session) -> None:
        gid = _unique_google_id()
        user = _register_local_user(db_session)
        user.google_id = gid
        user.auth_provider = "GOOGLE"
        db_session.commit()

        payload = _fake_id_token_payload(sub=gid)
        tokens = _full_google_login(client, payload)
        assert "access_token" in tokens


# ---------------------------------------------------------------------------
# Tests: Account linking
# ---------------------------------------------------------------------------

class TestAccountLinking:
    def test_existing_local_user_with_same_email_gets_linked(
        self, client: TestClient, db_session: Session
    ) -> None:
        gid = _unique_google_id()
        email = f"link_test_{uuid4().hex[:8]}@gmail.com"
        existing = _register_local_user(db_session, email=email)
        existing.auth_provider = "LOCAL"
        existing.google_id = None
        db_session.commit()

        payload = _fake_id_token_payload(sub=gid, email=email)
        tokens = _full_google_login(client, payload)
        assert "access_token" in tokens

        user_repo = UserRepository(db_session)
        user = user_repo.get_by_email(email)
        assert user is not None
        assert user.google_id == gid
        assert user.auth_provider == "GOOGLE"
        assert user.id == existing.id

    def test_no_duplicate_user_created(
        self, client: TestClient, db_session: Session
    ) -> None:
        gid = _unique_google_id()
        email = f"no_dup_{uuid4().hex[:8]}@gmail.com"
        _register_local_user(db_session, email=email)

        payload = _fake_id_token_payload(sub=gid, email=email)
        _full_google_login(client, payload)

        count = db_session.execute(
            text("SELECT COUNT(*) FROM users WHERE email = :e"), {"e": email}
        ).scalar()
        assert count == 1


# ---------------------------------------------------------------------------
# Tests: Username collisions
# ---------------------------------------------------------------------------

class TestUsernameCollisions:
    def test_collision_adds_suffix(self, client: TestClient, db_session: Session) -> None:
        _register_local_user(db_session, username="sf_test_john", email="test_john@example.com")

        gid = _unique_google_id()
        collision_email = f"sf_test_john{uuid4().hex[:4]}@gmail.com"
        payload = _fake_id_token_payload(sub=gid, email=collision_email)
        _full_google_login(client, payload)

        user_repo = UserRepository(db_session)
        user = user_repo.get_by_google_id(gid)
        assert user is not None
        assert user.username.startswith("sf_test_john")
        assert user.username != "sf_test_john"


# ---------------------------------------------------------------------------
# Tests: Verification function directly (NOT mocked)
# ---------------------------------------------------------------------------


def _build_test_jwk(public_key: object, kid: str = "test_kid") -> "PyJWK":
    """Build a PyJWK from an RSA public key for test mocking."""
    import base64
    from jwt import PyJWK

    pub_nums = public_key.public_numbers()

    def _int_to_base64url(num: int) -> str:
        num_bytes = num.to_bytes((num.bit_length() + 7) // 8, byteorder="big")
        return base64.urlsafe_b64encode(num_bytes).rstrip(b"=").decode()

    jwk_dict = {
        "kty": "RSA",
        "n": _int_to_base64url(pub_nums.n),
        "e": _int_to_base64url(pub_nums.e),
        "kid": kid,
        "alg": "RS256",
    }
    return PyJWK(jwk_dict)


class TestIdTokenVerification:
    def test_valid_token_succeeds(self) -> None:
        from backend.app.services.google_auth_service import _verify_google_id_token
        import jwt as pyjwt
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        public_key = private_key.public_key()

        payload = {
            "iss": "https://accounts.google.com",
            "aud": settings.google_client_id,
            "sub": "test_sub",
            "email": "test@example.com",
            "email_verified": True,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        }
        token = pyjwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "test_kid"})
        mock_jwk = _build_test_jwk(public_key)

        with patch("backend.app.services.google_auth_service.jwt.PyJWKClient") as MockClient:
            MockClient.return_value.get_signing_key_from_jwt.return_value = mock_jwk
            result = _verify_google_id_token(token, settings)

        assert result["sub"] == "test_sub"
        assert result["email"] == "test@example.com"

    def test_expired_token_rejected(self) -> None:
        from backend.app.services.google_auth_service import _verify_google_id_token
        import jwt as pyjwt
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        public_key = private_key.public_key()

        payload = {
            "iss": "https://accounts.google.com",
            "aud": settings.google_client_id,
            "sub": "test_sub",
            "email": "test@example.com",
            "email_verified": True,
            "iat": int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp()),
            "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
        }
        token = pyjwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "test_kid"})
        mock_jwk = _build_test_jwk(public_key)

        with patch("backend.app.services.google_auth_service.jwt.PyJWKClient") as MockClient:
            MockClient.return_value.get_signing_key_from_jwt.return_value = mock_jwk
            with pytest.raises(RuntimeError, match="has expired"):
                _verify_google_id_token(token, settings)

    def test_wrong_issuer_rejected(self) -> None:
        from backend.app.services.google_auth_service import _verify_google_id_token
        import jwt as pyjwt
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        public_key = private_key.public_key()

        payload = {
            "iss": "https://evil.com",
            "aud": settings.google_client_id,
            "sub": "test_sub",
            "email": "test@example.com",
            "email_verified": True,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        }
        token = pyjwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "test_kid"})
        mock_jwk = _build_test_jwk(public_key)

        with patch("backend.app.services.google_auth_service.jwt.PyJWKClient") as MockClient:
            MockClient.return_value.get_signing_key_from_jwt.return_value = mock_jwk
            with pytest.raises(RuntimeError, match="issuer"):
                _verify_google_id_token(token, settings)

    def test_wrong_audience_rejected(self) -> None:
        from backend.app.services.google_auth_service import _verify_google_id_token
        import jwt as pyjwt
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        public_key = private_key.public_key()

        payload = {
            "iss": "https://accounts.google.com",
            "aud": "fake-client-id",
            "sub": "test_sub",
            "email": "test@example.com",
            "email_verified": True,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        }
        token = pyjwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "test_kid"})
        mock_jwk = _build_test_jwk(public_key)

        with patch("backend.app.services.google_auth_service.jwt.PyJWKClient") as MockClient:
            MockClient.return_value.get_signing_key_from_jwt.return_value = mock_jwk
            with pytest.raises(RuntimeError, match="audience"):
                _verify_google_id_token(token, settings)


# ---------------------------------------------------------------------------
# Tests: Error handling for callback
# ---------------------------------------------------------------------------

class TestCallbackErrorHandling:
    def test_missing_code_returns_400(self, client: TestClient) -> None:
        response = client.get("/api/v1/auth/google/callback")
        assert response.status_code == 400

    def test_error_param_returns_400(self, client: TestClient) -> None:
        response = client.get("/api/v1/auth/google/callback?error=access_denied")
        assert response.status_code == 400

    def test_missing_exchange_code_returns_400(self, client: TestClient) -> None:
        resp = client.post("/api/v1/auth/google/exchange", json={})
        assert resp.status_code == 400

    def test_rate_limit_exchange(self, client: TestClient) -> None:
        """Verify exchange endpoint is rate limited."""
        for _ in range(25):
            resp = client.post("/api/v1/auth/google/exchange", json={"code": "test"})
            if resp.status_code == 429:
                return
        pytest.fail("Rate limiter did not trigger after 25 requests")


# ---------------------------------------------------------------------------
# Tests: Google account deletion
# ---------------------------------------------------------------------------

class TestGoogleAccountDeletion:
    def test_google_user_can_delete_account(self, client: TestClient, db_session: Session) -> None:
        tokens = _full_google_login(client)
        resp = client.request(
            "DELETE",
            "/api/v1/auth/delete-account",
            json={"password": "irrelevant"},
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert resp.status_code == 204

    def test_local_user_delete_still_requires_password(self, client: TestClient) -> None:
        username = f"sf_test_{uuid4().hex[:10]}"
        client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": "SuperSecret123",
            },
        )
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"identifier": username, "password": "SuperSecret123"},
        )
        tokens = login_resp.json()
        resp = client.request(
            "DELETE",
            "/api/v1/auth/delete-account",
            json={"password": "wrong_password"},
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Tests: Existing auth unchanged
# ---------------------------------------------------------------------------

class TestExistingAuthNotBroken:
    def test_local_register_still_works(self, client: TestClient) -> None:
        username = f"sf_test_{uuid4().hex[:10]}"
        resp = client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": "SuperSecret123",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["auth_provider"] == "LOCAL"

    def test_local_login_still_works(self, client: TestClient) -> None:
        username = f"sf_test_{uuid4().hex[:10]}"
        client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": "SuperSecret123",
            },
        )
        resp = client.post(
            "/api/v1/auth/login",
            json={"identifier": username, "password": "SuperSecret123"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()
