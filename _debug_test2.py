"""Debug test 2 - different patching strategies."""
import sys
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.api.deps import get_session
from backend.app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
db = TestingSessionLocal()

def override_get_session():
    yield db

app.dependency_overrides[get_session] = override_get_session

# Test 1: Patch GoogleAuthService.handle_google_callback
from backend.app.services.google_auth_service import GoogleAuthService
mock_user = type("MockUser", (), {"id": "test_id"})()
with patch.object(GoogleAuthService, "handle_google_callback", return_value=mock_user):
    client = TestClient(app)
    response = client.get("/api/v1/auth/google/callback?code=test_code")
    print(f"Test 1 - Patch class method: {response.status_code}")
    print(f"  Location: {response.headers.get('location', 'none')}")
    print(f"  Body: {response.text[:200]}")

# Test 2: Original module-level patches
mock_tokens = {"id_token": "fake_id_token", "access_token": "fake_access_token"}
payload = {"sub": "test", "email": "test@test.com", "email_verified": True}

with patch("backend.app.services.google_auth_service._exchange_code_for_tokens", return_value=mock_tokens), \
     patch("backend.app.services.google_auth_service._verify_google_id_token", return_value=payload):
    client2 = TestClient(app)
    response2 = client2.get("/api/v1/auth/google/callback?code=test_code")
    print(f"Test 2 - Module patches: {response2.status_code}")
    print(f"  Body: {response2.text[:200]}")

# Test 3: No patches
client3 = TestClient(app)
response3 = client3.get("/api/v1/auth/google/callback?code=test_code")
print(f"Test 3 - No patches: {response3.status_code}")

app.dependency_overrides.clear()
db.close()
