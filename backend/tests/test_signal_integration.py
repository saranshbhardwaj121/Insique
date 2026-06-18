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


# --- Authentication ---


def test_signals_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/signals/SFTESTA")
    assert response.status_code == 401


# --- Validation ---


def test_signals_invalid_ticker_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/signals/AA PL",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_signals_invalid_window_returns_422(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/signals/SFTESTA?rsi_window=1",
        headers=_auth_header(token),
    )
    assert response.status_code == 422


def test_signals_macd_slow_not_greater_than_fast_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/signals/SFTESTA?macd_fast=26&macd_slow=12",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_signals_sma_long_not_greater_than_short_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/signals/SFTESTA?sma_short=50&sma_long=20",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_signals_ema_long_not_greater_than_short_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/signals/SFTESTA?ema_short=26&ema_long=12",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_signals_rsi_oversold_ge_overbought_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/signals/SFTESTA?rsi_oversold=70&rsi_overbought=30",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_signals_unsupported_interval_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/signals/SFTESTA?interval=1h",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_signals_provider_failure_returns_502(client: TestClient) -> None:
    token = _register_and_login(client)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=RuntimeError("provider down"),
    ):
        response = client.get(
            "/api/v1/signals/SFTESTA",
            headers=_auth_header(token),
        )
    assert response.status_code == 502


def test_signals_empty_history_returns_502(client: TestClient) -> None:
    token = _register_and_login(client)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        return_value=FakeTicker(history_frame=pd.DataFrame()),
    ):
        response = client.get(
            "/api/v1/signals/SFTESTA",
            headers=_auth_header(token),
        )
    assert response.status_code == 502


# --- Signal Tests ---


def test_signals_insufficient_data_returns_neutral(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([100.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["rating"] == "NEUTRAL"
    assert payload["score"] == 0
    for sig in payload["signals"]:
        assert sig["action"] == "NEUTRAL"
        assert sig["reason"] == "insufficient_data"


def test_signals_uses_cached_data(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([100.0, 90.0, 80.0, 70.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        first_resp = client.get(
            "/api/v1/signals/SFTESTB",
            headers=_auth_header(token),
        )
    assert first_resp.status_code == 200
    assert first_resp.json()["provider"] == "yfinance"

    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=AssertionError("provider should not be called"),
    ):
        second_resp = client.get(
            "/api/v1/signals/SFTESTB",
            headers=_auth_header(token),
        )
    assert second_resp.status_code == 200
    assert second_resp.json()["provider"] == "database"
    assert second_resp.json()["cached"] is True


def test_signals_refresh_delegates_to_provider(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([100.0, 90.0, 80.0, 70.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTC?refresh=true",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    assert response.json()["provider"] == "yfinance"
    assert response.json()["cached"] is False


# --- RSI Signals ---


def test_rsi_strong_oversold_gives_buy(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([100.0, 90.0, 80.0, 70.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA?rsi_window=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    rsi_sig = next(s for s in payload["signals"] if s["name"] == "rsi")
    assert rsi_sig["action"] == "BUY"
    assert rsi_sig["score"] == 2
    assert rsi_sig["reason"] == "strong_oversold"


def test_rsi_strong_overbought_gives_sell(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([100.0, 110.0, 120.0, 130.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA?rsi_window=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    rsi_sig = next(s for s in payload["signals"] if s["name"] == "rsi")
    assert rsi_sig["action"] == "SELL"
    assert rsi_sig["score"] == -2
    assert rsi_sig["reason"] == "strong_overbought"


# --- MACD Signals ---


def test_macd_bullish_crossover_gives_buy(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([50.0, 50.0, 50.0, 50.0, 60.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA?macd_fast=2&macd_slow=3&macd_signal=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    macd_sig = next(s for s in payload["signals"] if s["name"] == "macd")
    assert macd_sig["action"] == "BUY"
    assert macd_sig["score"] == 2
    assert macd_sig["reason"] == "bullish_crossover"


def test_macd_bearish_crossover_gives_sell(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([50.0, 50.0, 50.0, 50.0, 40.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA?macd_fast=2&macd_slow=3&macd_signal=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    macd_sig = next(s for s in payload["signals"] if s["name"] == "macd")
    assert macd_sig["action"] == "SELL"
    assert macd_sig["score"] == -2
    assert macd_sig["reason"] == "bearish_crossover"


def test_macd_no_crossover_gives_neutral(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([50.0, 50.0, 50.0, 50.0, 50.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA?macd_fast=2&macd_slow=3&macd_signal=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    macd_sig = next(s for s in payload["signals"] if s["name"] == "macd")
    assert macd_sig["action"] == "NEUTRAL"
    assert macd_sig["score"] == 0
    assert macd_sig["reason"] == "no_crossover"


# --- SMA Trend Signals ---


def test_sma_uptrend_gives_buy(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([90.0, 100.0, 110.0, 120.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA?sma_short=2&sma_long=3",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    sma_sig = next(s for s in payload["signals"] if s["name"] == "sma_trend")
    assert sma_sig["action"] == "BUY"
    assert sma_sig["score"] == 1
    assert sma_sig["reason"] == "uptrend"


def test_sma_downtrend_gives_sell(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([120.0, 110.0, 100.0, 90.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA?sma_short=2&sma_long=3",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    sma_sig = next(s for s in payload["signals"] if s["name"] == "sma_trend")
    assert sma_sig["action"] == "SELL"
    assert sma_sig["score"] == -1
    assert sma_sig["reason"] == "downtrend"


# --- Aggregation ---


def test_strong_bullish_signals_give_buy_rating(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([100.0, 90.0, 80.0, 70.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA?rsi_window=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["rating"] == "BUY"
    assert payload["score"] >= 2


def test_strong_bearish_signals_give_sell_rating(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([100.0, 110.0, 120.0, 130.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA?rsi_window=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["rating"] == "SELL"
    assert payload["score"] <= -2


def test_conflicting_signals_give_neutral(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([100.0, 110.0, 120.0, 130.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA?rsi_window=2&sma_short=2&sma_long=3",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    rsi_sig = next(s for s in payload["signals"] if s["name"] == "rsi")
    sma_sig = next(s for s in payload["signals"] if s["name"] == "sma_trend")
    assert rsi_sig["action"] == "SELL"
    assert sma_sig["action"] == "BUY"
    assert payload["rating"] == "NEUTRAL"
    assert -2 < payload["score"] < 2


def test_signals_includes_all_signal_details(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _frame([100.0, 90.0, 80.0, 70.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA?rsi_window=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    signal_names = {s["name"] for s in payload["signals"]}
    assert signal_names == {"rsi", "macd", "sma_trend", "ema_trend"}
    assert payload["ticker"] == "SFTESTA"
    assert "rating" in payload
    assert "score" in payload
    assert "confidence" in payload
    assert "parameters" in payload
    assert "fetched_at" in payload
    assert "generated_at" in payload
