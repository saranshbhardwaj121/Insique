"""Debug test for callback route."""
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, ".")
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
client = TestClient(app)

# Test 1: basic route without patches
response = client.get("/api/v1/auth/google/callback?code=test_code")
print(f"Test 1 - No patches: {response.status_code}")

# Test 2: with patches
mock_tokens = {"id_token": "fake_id_token", "access_token": "fake_access_token"}
payload = {"sub": "test", "email": "test@test.com", "email_verified": True}

with patch("backend.app.services.google_auth_service._exchange_code_for_tokens", return_value=mock_tokens), \
     patch("backend.app.services.google_auth_service._verify_google_id_token", return_value=payload):
    response = client.get("/api/v1/auth/google/callback?code=test_code")
    print(f"Test 2 - With patches: {response.status_code}")
    if response.status_code == 404:
        print(f"  Body: {response.text[:500]}")
    else:
        print(f"  Location: {response.headers.get('location', 'none')}")

app.dependency_overrides.clear()
db.close()
