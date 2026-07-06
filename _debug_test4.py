"""Minimal reproduction - test callback with patches."""
import sys
sys.path.insert(0, ".")
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

# Import the router and its dependencies
from backend.app.api.router import api_router
from backend.app.core.config import get_settings

settings = get_settings()

# Create a fresh app
test_app = FastAPI()
test_app.include_router(api_router, prefix="/api/v1")

# Print all routes
print("=== All routes ===")
for r in test_app.routes:
    path = getattr(r, "path", "")
    methods = getattr(r, "methods", set())
    if path:
        print(f"  {methods} {path}")

# Override session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.api.deps import get_session
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
db = TestingSessionLocal()

def override_get_session():
    yield db

test_app.dependency_overrides[get_session] = override_get_session

c = TestClient(test_app)

# Test without patches first
r = c.get("/api/v1/auth/google/callback?code=test")
print(f"\nNo patches: {r.status_code}")

# Create a new client for patched test (to avoid any state issues)
mock_tokens = {"id_token": "fake_id_token", "access_token": "fake_access_token"}
payload = {"sub": "test", "email": "test@test.com", "email_verified": True}

with patch("backend.app.services.google_auth_service._exchange_code_for_tokens", return_value=mock_tokens), \
     patch("backend.app.services.google_auth_service._verify_google_id_token", return_value=payload):
    c2 = TestClient(test_app)
    r2 = c2.get("/api/v1/auth/google/callback?code=test_code")
    print(f"With patches: {r2.status_code}")
    print(f"  Body: {r2.text[:300]}")

test_app.dependency_overrides.clear()
db.close()
