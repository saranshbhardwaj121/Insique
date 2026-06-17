from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.api.deps import get_session
from backend.app.core.config import get_settings
from backend.app.main import app
from backend.app.models.base import Base
from backend.app.models.user import User

settings = get_settings()
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def prepare_schema() -> None:
    Base.metadata.create_all(bind=engine)


@pytest.fixture()
def db_session() -> Session:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.query(User).filter(User.username.like("sf_test_%")).delete(
            synchronize_session=False
        )
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


def _register_and_login(client: TestClient) -> tuple[str, str]:
    username = f"sf_test_{uuid4().hex[:10]}"
    email = f"{username}@example.com"
    password = "SuperSecret123"
    client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"identifier": username, "password": password},
    )
    tokens = login_resp.json()
    return tokens["access_token"], username, email


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# --- Unauthenticated access ---


def test_list_watchlists_unauthenticated_returns_401(client: TestClient) -> None:
    resp = client.get("/api/v1/watchlists")
    assert resp.status_code == 401


def test_create_watchlist_unauthenticated_returns_401(client: TestClient) -> None:
    resp = client.post("/api/v1/watchlists", json={"name": "My Watchlist"})
    assert resp.status_code == 401


# --- Create ---


def test_create_watchlist_success(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    resp = client.post(
        "/api/v1/watchlists",
        json={"name": "Tech Stocks"},
        headers=_auth_header(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Tech Stocks"
    assert "id" in data
    assert data["items"] == []


def test_create_watchlist_empty_name_rejected(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    resp = client.post(
        "/api/v1/watchlists",
        json={"name": "   "},
        headers=_auth_header(token),
    )
    assert resp.status_code == 400


def test_create_watchlist_whitespace_name_trimmed_to_empty_rejected(
    client: TestClient,
) -> None:
    token, _, _ = _register_and_login(client)
    resp = client.post(
        "/api/v1/watchlists",
        json={"name": "   "},
        headers=_auth_header(token),
    )
    assert resp.status_code == 400


def test_create_duplicate_watchlist_name_rejected(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    client.post(
        "/api/v1/watchlists",
        json={"name": "My List"},
        headers=_auth_header(token),
    )
    resp = client.post(
        "/api/v1/watchlists",
        json={"name": "My List"},
        headers=_auth_header(token),
    )
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]


def test_create_watchlist_same_name_different_users_allowed(
    client: TestClient,
) -> None:
    token1, _, _ = _register_and_login(client)
    token2, _, _ = _register_and_login(client)
    resp1 = client.post(
        "/api/v1/watchlists",
        json={"name": "Shared Name"},
        headers=_auth_header(token1),
    )
    assert resp1.status_code == 201
    resp2 = client.post(
        "/api/v1/watchlists",
        json={"name": "Shared Name"},
        headers=_auth_header(token2),
    )
    assert resp2.status_code == 201


# --- List ---


def test_list_watchlists_returns_only_own(client: TestClient) -> None:
    token1, _, _ = _register_and_login(client)
    token2, _, _ = _register_and_login(client)
    client.post(
        "/api/v1/watchlists",
        json={"name": "User1 List"},
        headers=_auth_header(token1),
    )
    client.post(
        "/api/v1/watchlists",
        json={"name": "User2 List"},
        headers=_auth_header(token2),
    )
    resp1 = client.get("/api/v1/watchlists", headers=_auth_header(token1))
    assert resp1.status_code == 200
    names1 = [w["name"] for w in resp1.json()]
    assert "User1 List" in names1
    assert "User2 List" not in names1


def test_list_watchlists_returns_deterministic_order(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    client.post(
        "/api/v1/watchlists",
        json={"name": "B"},
        headers=_auth_header(token),
    )
    client.post(
        "/api/v1/watchlists",
        json={"name": "A"},
        headers=_auth_header(token),
    )
    client.post(
        "/api/v1/watchlists",
        json={"name": "C"},
        headers=_auth_header(token),
    )
    resp = client.get("/api/v1/watchlists", headers=_auth_header(token))
    assert resp.status_code == 200
    names = [w["name"] for w in resp.json()]
    assert names == ["B", "A", "C"]


def test_list_watchlists_empty(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    resp = client.get("/api/v1/watchlists", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json() == []


# --- Get ---


def test_get_watchlist_success(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "My List"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.get(
        f"/api/v1/watchlists/{watchlist_id}",
        headers=_auth_header(token),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "My List"


def test_get_others_watchlist_returns_404(client: TestClient) -> None:
    token1, _, _ = _register_and_login(client)
    token2, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "Secret"},
        headers=_auth_header(token1),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.get(
        f"/api/v1/watchlists/{watchlist_id}",
        headers=_auth_header(token2),
    )
    assert resp.status_code == 404


def test_get_nonexistent_watchlist_returns_404(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = client.get(
        f"/api/v1/watchlists/{fake_id}",
        headers=_auth_header(token),
    )
    assert resp.status_code == 404


# --- Rename ---


def test_rename_watchlist_success(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "Old Name"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.patch(
        f"/api/v1/watchlists/{watchlist_id}",
        json={"name": "New Name"},
        headers=_auth_header(token),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


def test_rename_to_duplicate_rejected(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    client.post(
        "/api/v1/watchlists",
        json={"name": "List A"},
        headers=_auth_header(token),
    )
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "List B"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.patch(
        f"/api/v1/watchlists/{watchlist_id}",
        json={"name": "List A"},
        headers=_auth_header(token),
    )
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]


def test_rename_others_watchlist_returns_404(client: TestClient) -> None:
    token1, _, _ = _register_and_login(client)
    token2, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "Mine"},
        headers=_auth_header(token1),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.patch(
        f"/api/v1/watchlists/{watchlist_id}",
        json={"name": "Yours Now"},
        headers=_auth_header(token2),
    )
    assert resp.status_code == 404


def test_rename_to_empty_rejected(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "Valid"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.patch(
        f"/api/v1/watchlists/{watchlist_id}",
        json={"name": "   "},
        headers=_auth_header(token),
    )
    assert resp.status_code == 400


# --- Delete ---


def test_delete_watchlist_success(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "To Delete"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.delete(
        f"/api/v1/watchlists/{watchlist_id}",
        headers=_auth_header(token),
    )
    assert resp.status_code == 204
    get_resp = client.get(
        f"/api/v1/watchlists/{watchlist_id}",
        headers=_auth_header(token),
    )
    assert get_resp.status_code == 404


def test_delete_others_watchlist_returns_404(client: TestClient) -> None:
    token1, _, _ = _register_and_login(client)
    token2, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "Not Yours"},
        headers=_auth_header(token1),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.delete(
        f"/api/v1/watchlists/{watchlist_id}",
        headers=_auth_header(token2),
    )
    assert resp.status_code == 404


def test_delete_nonexistent_watchlist_returns_404(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = client.delete(
        f"/api/v1/watchlists/{fake_id}",
        headers=_auth_header(token),
    )
    assert resp.status_code == 404


# --- Add ticker ---


def test_add_ticker_success(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "My List"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.post(
        f"/api/v1/watchlists/{watchlist_id}/items",
        json={"ticker": "AAPL"},
        headers=_auth_header(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["ticker"] == "AAPL"


def test_add_ticker_normalizes_uppercase(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "My List"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.post(
        f"/api/v1/watchlists/{watchlist_id}/items",
        json={"ticker": "  aapl  "},
        headers=_auth_header(token),
    )
    assert resp.status_code == 201
    tickers = [i["ticker"] for i in resp.json()["items"]]
    assert "AAPL" in tickers


def test_add_duplicate_ticker_rejected(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "My List"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    client.post(
        f"/api/v1/watchlists/{watchlist_id}/items",
        json={"ticker": "AAPL"},
        headers=_auth_header(token),
    )
    resp = client.post(
        f"/api/v1/watchlists/{watchlist_id}/items",
        json={"ticker": "aapl"},
        headers=_auth_header(token),
    )
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]


def test_add_ticker_to_others_watchlist_returns_404(client: TestClient) -> None:
    token1, _, _ = _register_and_login(client)
    token2, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "Mine"},
        headers=_auth_header(token1),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.post(
        f"/api/v1/watchlists/{watchlist_id}/items",
        json={"ticker": "AAPL"},
        headers=_auth_header(token2),
    )
    assert resp.status_code == 404


def test_add_ticker_empty_rejected(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "My List"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.post(
        f"/api/v1/watchlists/{watchlist_id}/items",
        json={"ticker": "   "},
        headers=_auth_header(token),
    )
    assert resp.status_code == 400


def test_add_ticker_items_ordered_deterministically(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "My List"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    for ticker in ["MSFT", "AAPL", "GOOG"]:
        client.post(
            f"/api/v1/watchlists/{watchlist_id}/items",
            json={"ticker": ticker},
            headers=_auth_header(token),
        )
    resp = client.get(
        f"/api/v1/watchlists/{watchlist_id}",
        headers=_auth_header(token),
    )
    assert resp.status_code == 200
    tickers = [i["ticker"] for i in resp.json()["items"]]
    assert tickers == ["AAPL", "GOOG", "MSFT"]


# --- Remove ticker ---


def test_remove_ticker_success(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "My List"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    client.post(
        f"/api/v1/watchlists/{watchlist_id}/items",
        json={"ticker": "AAPL"},
        headers=_auth_header(token),
    )
    resp = client.delete(
        f"/api/v1/watchlists/{watchlist_id}/items/AAPL",
        headers=_auth_header(token),
    )
    assert resp.status_code == 204
    get_resp = client.get(
        f"/api/v1/watchlists/{watchlist_id}",
        headers=_auth_header(token),
    )
    assert len(get_resp.json()["items"]) == 0


def test_remove_ticker_normalizes_case(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "My List"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    client.post(
        f"/api/v1/watchlists/{watchlist_id}/items",
        json={"ticker": "AAPL"},
        headers=_auth_header(token),
    )
    resp = client.delete(
        f"/api/v1/watchlists/{watchlist_id}/items/aapl",
        headers=_auth_header(token),
    )
    assert resp.status_code == 204


def test_remove_missing_ticker_returns_404(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "My List"},
        headers=_auth_header(token),
    )
    watchlist_id = create_resp.json()["id"]
    resp = client.delete(
        f"/api/v1/watchlists/{watchlist_id}/items/NONEXIST",
        headers=_auth_header(token),
    )
    assert resp.status_code == 404


def test_remove_ticker_from_others_watchlist_returns_404(
    client: TestClient,
) -> None:
    token1, _, _ = _register_and_login(client)
    token2, _, _ = _register_and_login(client)
    create_resp = client.post(
        "/api/v1/watchlists",
        json={"name": "Mine"},
        headers=_auth_header(token1),
    )
    watchlist_id = create_resp.json()["id"]
    client.post(
        f"/api/v1/watchlists/{watchlist_id}/items",
        json={"ticker": "AAPL"},
        headers=_auth_header(token1),
    )
    resp = client.delete(
        f"/api/v1/watchlists/{watchlist_id}/items/AAPL",
        headers=_auth_header(token2),
    )
    assert resp.status_code == 404
