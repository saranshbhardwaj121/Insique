from uuid import uuid4
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.api.deps import get_session
from backend.app.core.config import get_settings
from backend.app.main import app
from backend.app.models.base import Base
from backend.app.models.market_data import MarketData
from backend.app.models.user import User

settings = get_settings()
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class FakeTicker:
    def __init__(
        self,
        fast_info: dict[str, object] | None = None,
        info: dict[str, object] | None = None,
        history_frame: pd.DataFrame | None = None,
    ) -> None:
        self.fast_info = fast_info or {}
        self.info = info or {}
        self._history_frame = history_frame if history_frame is not None else pd.DataFrame()

    def history(self, **_: object) -> pd.DataFrame:
        return self._history_frame


@pytest.fixture(scope="session", autouse=True)
def prepare_schema() -> None:
    Base.metadata.create_all(bind=engine)


@pytest.fixture()
def db_session() -> Session:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.query(MarketData).filter(MarketData.ticker.like("SFTEST%")).delete(
            synchronize_session=False,
        )
        db.query(User).filter(User.username.like("sf_test_%")).delete(
            synchronize_session=False,
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


def _register_and_login(client: TestClient) -> str:
    username = f"sf_test_{uuid4().hex[:10]}"
    email = f"{username}@example.com"
    password = "SuperSecret123"
    client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": username, "password": password},
    )
    return response.json()["access_token"]


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _frame(closes: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": closes,
            "High": [x + 2.0 for x in closes],
            "Low": [x - 2.0 for x in closes],
            "Close": closes,
            "Volume": [1000] * len(closes),
        },
        index=pd.to_datetime(
            [f"2026-01-{str(i+2).zfill(2)}" for i in range(len(closes))],
        ),
    )


def _create_watchlist(client: TestClient, token: str, name: str) -> str:
    resp = client.post(
        "/api/v1/watchlists",
        json={"name": name},
        headers=_auth_header(token),
    )
    return resp.json()["id"]


def _add_ticker(client: TestClient, token: str, watchlist_id: str, ticker: str) -> None:
    client.post(
        f"/api/v1/watchlists/{watchlist_id}/items",
        json={"ticker": ticker},
        headers=_auth_header(token),
    )


# --- Auth & Ownership ---


def test_watchlist_signals_unauthenticated_returns_401(client: TestClient) -> None:
    watchlist_id = "00000000-0000-0000-0000-000000000000"
    resp = client.get(f"/api/v1/watchlists/{watchlist_id}/signals")
    assert resp.status_code == 401


def test_watchlist_signals_others_watchlist_returns_404(client: TestClient) -> None:
    token1 = _register_and_login(client)
    token2 = _register_and_login(client)
    wl_id = _create_watchlist(client, token1, "Private")
    resp = client.get(
        f"/api/v1/watchlists/{wl_id}/signals",
        headers=_auth_header(token2),
    )
    assert resp.status_code == 404


def test_watchlist_signals_nonexistent_returns_404(client: TestClient) -> None:
    token = _register_and_login(client)
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = client.get(
        f"/api/v1/watchlists/{fake_id}/signals",
        headers=_auth_header(token),
    )
    assert resp.status_code == 404


# --- Empty watchlist ---


def test_watchlist_signals_empty_returns_empty_signals(client: TestClient) -> None:
    token = _register_and_login(client)
    wl_id = _create_watchlist(client, token, "Empty")
    resp = client.get(
        f"/api/v1/watchlists/{wl_id}/signals",
        headers=_auth_header(token),
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["signals"] == []
    assert payload["watchlist_name"] == "Empty"
    assert payload["watchlist_id"] == wl_id
    assert "generated_at" in payload


# --- Full signal results ---


def test_watchlist_signals_returns_all_tickers(client: TestClient) -> None:
    token = _register_and_login(client)
    wl_id = _create_watchlist(client, token, "Tech")
    for ticker in ["SFTESTA", "SFTESTB", "SFTESTC"]:
        _add_ticker(client, token, wl_id, ticker)

    frame = _frame([100.0, 90.0, 80.0, 70.0])
    fake = FakeTicker(history_frame=frame)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        return_value=fake,
    ):
        resp = client.get(
            f"/api/v1/watchlists/{wl_id}/signals",
            headers=_auth_header(token),
        )

    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload["signals"]) == 3
    tickers = [s["ticker"] for s in payload["signals"]]
    assert tickers == ["SFTESTA", "SFTESTB", "SFTESTC"]


def test_watchlist_signals_deterministic_order(client: TestClient) -> None:
    token = _register_and_login(client)
    wl_id = _create_watchlist(client, token, "Mixed")
    for ticker in ["SFTESTC", "SFTESTA", "SFTESTB"]:
        _add_ticker(client, token, wl_id, ticker)

    frame = _frame([100.0, 90.0, 80.0, 70.0])
    fake = FakeTicker(history_frame=frame)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        return_value=fake,
    ):
        resp = client.get(
            f"/api/v1/watchlists/{wl_id}/signals",
            headers=_auth_header(token),
        )

    assert resp.status_code == 200
    tickers = [s["ticker"] for s in resp.json()["signals"]]
    assert tickers == ["SFTESTA", "SFTESTB", "SFTESTC"]


def test_watchlist_signals_includes_signal_data(client: TestClient) -> None:
    token = _register_and_login(client)
    wl_id = _create_watchlist(client, token, "Test")
    _add_ticker(client, token, wl_id, "SFTESTA")

    frame = _frame([100.0, 110.0, 120.0, 130.0])
    fake = FakeTicker(history_frame=frame)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        return_value=fake,
    ):
        resp = client.get(
            f"/api/v1/watchlists/{wl_id}/signals?rsi_window=2",
            headers=_auth_header(token),
        )

    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload["signals"]) == 1
    entry = payload["signals"][0]
    assert entry["ticker"] == "SFTESTA"
    assert entry["error"] is None
    summary = entry["summary"]
    assert summary["rating"] == "SELL"
    assert summary["score"] <= -2
    assert summary["ticker"] == "SFTESTA"
    assert "signals" in summary
    assert "parameters" in payload
    assert "generated_at" in payload


# --- Partial failures ---


def test_watchlist_signals_partial_provider_failure(client: TestClient) -> None:
    token = _register_and_login(client)
    wl_id = _create_watchlist(client, token, "PartialFailure")
    for ticker in ["SFTEST1", "SFTESTBROKEN", "SFTEST3"]:
        _add_ticker(client, token, wl_id, ticker)

    frame = _frame([100.0, 90.0, 80.0, 70.0])
    fake = FakeTicker(history_frame=frame)

    def fake_ticker_factory(ticker: str) -> FakeTicker:
        if ticker == "SFTESTBROKEN":
            raise RuntimeError("provider error")
        return fake

    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=fake_ticker_factory,
    ):
        resp = client.get(
            f"/api/v1/watchlists/{wl_id}/signals",
            headers=_auth_header(token),
        )

    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload["signals"]) == 3
    assert payload["signals"][0]["ticker"] == "SFTEST1"
    assert payload["signals"][0]["summary"] is not None
    assert payload["signals"][0]["error"] is None
    assert payload["signals"][1]["ticker"] == "SFTEST3"
    assert payload["signals"][1]["summary"] is not None
    assert payload["signals"][1]["error"] is None
    assert payload["signals"][2]["ticker"] == "SFTESTBROKEN"
    assert payload["signals"][2]["summary"] is None
    assert payload["signals"][2]["error"] is not None


def test_watchlist_signals_all_provider_failures(client: TestClient) -> None:
    token = _register_and_login(client)
    wl_id = _create_watchlist(client, token, "AllBad")
    for ticker in ["SFTESTX", "SFTESTY"]:
        _add_ticker(client, token, wl_id, ticker)

    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=RuntimeError("provider down"),
    ):
        resp = client.get(
            f"/api/v1/watchlists/{wl_id}/signals",
            headers=_auth_header(token),
        )

    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload["signals"]) == 2
    for entry in payload["signals"]:
        assert entry["summary"] is None
        assert entry["error"] is not None


# --- Query validation ---


def test_watchlist_signals_invalid_rsi_window_returns_422(client: TestClient) -> None:
    token = _register_and_login(client)
    wl_id = _create_watchlist(client, token, "Test")
    resp = client.get(
        f"/api/v1/watchlists/{wl_id}/signals?rsi_window=1",
        headers=_auth_header(token),
    )
    assert resp.status_code == 422


def test_watchlist_signals_macd_slow_not_greater_than_fast_returns_400(
    client: TestClient,
) -> None:
    token = _register_and_login(client)
    wl_id = _create_watchlist(client, token, "Test")
    resp = client.get(
        f"/api/v1/watchlists/{wl_id}/signals?macd_fast=26&macd_slow=12",
        headers=_auth_header(token),
    )
    assert resp.status_code == 400


def test_watchlist_signals_sma_long_not_greater_than_short_returns_400(
    client: TestClient,
) -> None:
    token = _register_and_login(client)
    wl_id = _create_watchlist(client, token, "Test")
    resp = client.get(
        f"/api/v1/watchlists/{wl_id}/signals?sma_short=50&sma_long=20",
        headers=_auth_header(token),
    )
    assert resp.status_code == 400


def test_watchlist_signals_ema_long_not_greater_than_short_returns_400(
    client: TestClient,
) -> None:
    token = _register_and_login(client)
    wl_id = _create_watchlist(client, token, "Test")
    resp = client.get(
        f"/api/v1/watchlists/{wl_id}/signals?ema_short=26&ema_long=12",
        headers=_auth_header(token),
    )
    assert resp.status_code == 400


def test_watchlist_signals_rsi_oversold_ge_overbought_returns_400(
    client: TestClient,
) -> None:
    token = _register_and_login(client)
    wl_id = _create_watchlist(client, token, "Test")
    resp = client.get(
        f"/api/v1/watchlists/{wl_id}/signals?rsi_oversold=70&rsi_overbought=30",
        headers=_auth_header(token),
    )
    assert resp.status_code == 400
