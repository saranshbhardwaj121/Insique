from uuid import uuid4
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.api.deps import get_session
from backend.app.core.config import get_settings
from backend.app.main import app
from backend.app.models.base import Base
from backend.app.models.user import User


class FakeFastInfo:
    def __init__(self, price: float | None = None) -> None:
        self._price = price

    @property
    def last_price(self) -> float | None:
        return self._price

    @property
    def lastPrice(self) -> float | None:
        return self._price


class FakeTicker:
    def __init__(self, price: float | None = None) -> None:
        self.fast_info = FakeFastInfo(price)
        self.info = {"currency": "USD", "shortName": "Fake Corp"} if price else {}

    def history(self, **_: object) -> object:
        import pandas as pd
        return pd.DataFrame()


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


def _register_and_login(client: TestClient) -> tuple[str, str, str]:
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


def _create_holding(
    client: TestClient, token: str, ticker: str = "AAPL", quantity: float = 10, avg_cost: float = 150.0
) -> dict:
    resp = client.post(
        "/api/v1/portfolio/holdings",
        json={"ticker": ticker, "quantity": quantity, "average_cost_basis": avg_cost},
        headers=_auth_header(token),
    )
    assert resp.status_code == 201
    return resp.json()


# --- Unauthenticated access ---


def test_list_holdings_unauthenticated_returns_401(client: TestClient) -> None:
    resp = client.get("/api/v1/portfolio/holdings")
    assert resp.status_code == 401


def test_add_holding_unauthenticated_returns_401(client: TestClient) -> None:
    resp = client.post("/api/v1/portfolio/holdings", json={"ticker": "AAPL", "quantity": 10, "average_cost_basis": 150})
    assert resp.status_code == 401


def test_update_holding_unauthenticated_returns_401(client: TestClient) -> None:
    resp = client.patch("/api/v1/portfolio/holdings/00000000-0000-0000-0000-000000000000", json={"quantity": 5})
    assert resp.status_code == 401


def test_delete_holding_unauthenticated_returns_401(client: TestClient) -> None:
    resp = client.delete("/api/v1/portfolio/holdings/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401


def test_portfolio_summary_unauthenticated_returns_401(client: TestClient) -> None:
    resp = client.get("/api/v1/portfolio/summary")
    assert resp.status_code == 401


# --- Create ---


def test_add_holding_success(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    data = _create_holding(client, token, "MSFT", 5, 340.0)
    assert data["ticker"] == "MSFT"
    assert data["quantity"] == 5.0
    assert data["average_cost_basis"] == 340.0
    assert "id" in data


def test_add_holding_duplicate_ticker_rejected(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    _create_holding(client, token, "AAPL", 10, 150.0)
    resp = client.post(
        "/api/v1/portfolio/holdings",
        json={"ticker": "AAPL", "quantity": 5, "average_cost_basis": 200.0},
        headers=_auth_header(token),
    )
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"].lower()


def test_add_holding_invalid_quantity_rejected(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    resp = client.post(
        "/api/v1/portfolio/holdings",
        json={"ticker": "AAPL", "quantity": -1, "average_cost_basis": 150.0},
        headers=_auth_header(token),
    )
    assert resp.status_code == 422


def test_add_holding_zero_avg_cost_rejected(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    resp = client.post(
        "/api/v1/portfolio/holdings",
        json={"ticker": "AAPL", "quantity": 10, "average_cost_basis": 0},
        headers=_auth_header(token),
    )
    assert resp.status_code == 422


def test_add_holding_normalizes_ticker(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    data = _create_holding(client, token, "  aapl  ", 10, 150.0)
    assert data["ticker"] == "AAPL"


# --- List ---


def test_list_holdings_empty(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    resp = client.get("/api/v1/portfolio/holdings", headers=_auth_header(token))
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_holdings_returns_all(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    _create_holding(client, token, "AAPL", 10, 150.0)
    _create_holding(client, token, "MSFT", 5, 340.0)
    resp = client.get("/api/v1/portfolio/holdings", headers=_auth_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    tickers = [h["ticker"] for h in data]
    assert tickers == ["AAPL", "MSFT"]


def test_list_holdings_returns_only_own(client: TestClient) -> None:
    token1, _, _ = _register_and_login(client)
    token2, _, _ = _register_and_login(client)
    _create_holding(client, token1, "AAPL", 10, 150.0)
    _create_holding(client, token2, "MSFT", 5, 340.0)
    resp1 = client.get("/api/v1/portfolio/holdings", headers=_auth_header(token1))
    assert len(resp1.json()) == 1
    assert resp1.json()[0]["ticker"] == "AAPL"
    resp2 = client.get("/api/v1/portfolio/holdings", headers=_auth_header(token2))
    assert len(resp2.json()) == 1
    assert resp2.json()[0]["ticker"] == "MSFT"


# --- Update ---


def test_update_holding_quantity(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    data = _create_holding(client, token, "AAPL", 10, 150.0)
    holding_id = data["id"]
    resp = client.patch(
        f"/api/v1/portfolio/holdings/{holding_id}",
        json={"quantity": 20},
        headers=_auth_header(token),
    )
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 20.0
    assert resp.json()["average_cost_basis"] == 150.0


def test_update_holding_avg_cost(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    data = _create_holding(client, token, "AAPL", 10, 150.0)
    holding_id = data["id"]
    resp = client.patch(
        f"/api/v1/portfolio/holdings/{holding_id}",
        json={"average_cost_basis": 175.0},
        headers=_auth_header(token),
    )
    assert resp.status_code == 200
    assert resp.json()["average_cost_basis"] == 175.0
    assert resp.json()["quantity"] == 10.0


def test_update_holding_not_found(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    resp = client.patch(
        "/api/v1/portfolio/holdings/00000000-0000-0000-0000-000000000000",
        json={"quantity": 5},
        headers=_auth_header(token),
    )
    assert resp.status_code == 404


def test_update_holding_wrong_owner(client: TestClient) -> None:
    token1, _, _ = _register_and_login(client)
    token2, _, _ = _register_and_login(client)
    data = _create_holding(client, token1, "AAPL", 10, 150.0)
    resp = client.patch(
        f"/api/v1/portfolio/holdings/{data['id']}",
        json={"quantity": 5},
        headers=_auth_header(token2),
    )
    assert resp.status_code == 404


# --- Delete ---


def test_delete_holding_success(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    data = _create_holding(client, token, "AAPL", 10, 150.0)
    resp = client.delete(
        f"/api/v1/portfolio/holdings/{data['id']}",
        headers=_auth_header(token),
    )
    assert resp.status_code == 204
    list_resp = client.get("/api/v1/portfolio/holdings", headers=_auth_header(token))
    assert list_resp.json() == []


def test_delete_holding_not_found(client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    resp = client.delete(
        "/api/v1/portfolio/holdings/00000000-0000-0000-0000-000000000000",
        headers=_auth_header(token),
    )
    assert resp.status_code == 404


def test_delete_holding_wrong_owner(client: TestClient) -> None:
    token1, _, _ = _register_and_login(client)
    token2, _, _ = _register_and_login(client)
    data = _create_holding(client, token1, "AAPL", 10, 150.0)
    resp = client.delete(
        f"/api/v1/portfolio/holdings/{data['id']}",
        headers=_auth_header(token2),
    )
    assert resp.status_code == 404


# --- Summary ---


@patch("yfinance.Ticker")
def test_portfolio_summary_with_holdings(mock_ticker: object, client: TestClient) -> None:
    mock_ticker.return_value = FakeTicker(price=200.0)
    token, _, _ = _register_and_login(client)
    _create_holding(client, token, "AAPL", 10, 150.0)
    resp = client.get("/api/v1/portfolio/summary", headers=_auth_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_holdings"] == 1
    assert data["total_cost_basis"] == 1500.0
    assert data["total_market_value"] == 2000.0
    assert data["total_profit_loss"] == 500.0
    assert data["profitable_holdings"] == 1
    assert data["losing_holdings"] == 0
    assert len(data["holdings"]) == 1
    h = data["holdings"][0]
    assert h["ticker"] == "AAPL"
    assert h["current_price"] == 200.0
    assert h["market_value"] == 2000.0
    assert h["profit_loss"] == 500.0
    assert h["profit_loss_percent"] == pytest.approx(33.33, rel=0.1)
    assert h["allocation_percent"] == 100.0


@patch("yfinance.Ticker")
def test_portfolio_summary_multiple_holdings(mock_ticker: object, client: TestClient) -> None:
    mock_ticker.return_value = FakeTicker(price=100.0)
    token, _, _ = _register_and_login(client)
    _create_holding(client, token, "AAPL", 10, 80.0)
    _create_holding(client, token, "MSFT", 5, 120.0)
    resp = client.get("/api/v1/portfolio/summary", headers=_auth_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_holdings"] == 2
    assert data["total_cost_basis"] == 1400.0
    assert data["total_market_value"] == 1500.0
    assert data["total_profit_loss"] == 100.0


@patch("yfinance.Ticker")
def test_portfolio_summary_empty(mock_ticker: object, client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    resp = client.get("/api/v1/portfolio/summary", headers=_auth_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_holdings"] == 0
    assert data["total_market_value"] == 0.0
    assert data["total_cost_basis"] == 0.0
    assert data["holdings"] == []


@patch("yfinance.Ticker")
def test_portfolio_summary_price_fetch_failure(mock_ticker: object, client: TestClient) -> None:
    mock_ticker.side_effect = Exception("API failure")
    token, _, _ = _register_and_login(client)
    _create_holding(client, token, "AAPL", 10, 150.0)
    resp = client.get("/api/v1/portfolio/summary", headers=_auth_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_holdings"] == 1
    assert data["total_market_value"] == 0.0
    assert data["total_cost_basis"] == 1500.0
    assert data["holdings"][0]["current_price"] is None
    assert data["holdings"][0]["market_value"] is None


@patch("yfinance.Ticker")
def test_portfolio_summary_profitable_and_losing(mock_ticker: object, client: TestClient) -> None:
    token, _, _ = _register_and_login(client)
    _create_holding(client, token, "AAPL", 10, 150.0)
    _create_holding(client, token, "MSFT", 5, 340.0)

    original_ticker = FakeTicker

    class SideEffectTicker:
        def __new__(cls, ticker: str) -> FakeTicker:
            prices = {"AAPL": 200.0, "MSFT": 300.0}
            return original_ticker(price=prices.get(ticker, 0))

    mock_ticker.side_effect = SideEffectTicker
    resp = client.get("/api/v1/portfolio/summary", headers=_auth_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["profitable_holdings"] == 1
    assert data["losing_holdings"] == 1
    assert data["total_profit_loss"] == pytest.approx(300.0, abs=1)
