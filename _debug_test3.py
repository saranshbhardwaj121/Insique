"""Debug test 3 - fresh app for each test."""
import sys
sys.path.insert(0, ".")
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import get_settings
from backend.app.api.deps import get_session

settings = get_settings()
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
db = TestingSessionLocal()

def override_get_session():
    yield db

mock_tokens = {"id_token": "fake_id_token", "access_token": "fake_access_token"}
payload = {"sub": "test", "email": "test@test.com", "email_verified": True}

# Fresh import for each test
import importlib

# Test 2 - Module patches with fresh modules
with patch("backend.app.services.google_auth_service._exchange_code_for_tokens", return_value=mock_tokens), \
     patch("backend.app.services.google_auth_service._verify_google_id_token", return_value=payload):
    # Import AFTER patches are active - this might help
    from backend.app.api.v1.routes import auth as auth_routes
    from backend.app.api.router import api_router
    
    test_app = FastAPI()
    test_app.include_router(api_router, prefix="/api/v1")
    
    # Check routes
    print("Routes:")
    for r in test_app.routes:
        if hasattr(r, "path") and "google" in (getattr(r, "path", "") or ""):
            print(f"  {r.path}")
    
    test_app.dependency_overrides[get_session] = override_get_session
    c = TestClient(test_app)
    r = c.get("/api/v1/auth/google/callback?code=test_code")
    print(f"Test A - Module patches, fresh app: {r.status_code}")
    print(f"  Body: {r.text[:300]}")

app.dependency_overrides.clear()
db.close()
