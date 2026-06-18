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


def _history_frame(close: float = 101.0) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [close, close + 1.0],
            "Volume": [1000, 2000],
        },
        index=pd.to_datetime(["2026-01-02", "2026-01-03"]),
    )


# --- Authentication ---


def test_sma_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/SFTESTA/sma")
    assert response.status_code == 401


def test_ema_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/SFTESTA/ema")
    assert response.status_code == 401


# --- Validation ---


def test_sma_invalid_ticker_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/AA PL/sma",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_sma_invalid_window_too_small_returns_422(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/sma?window=1",
        headers=_auth_header(token),
    )
    assert response.status_code == 422


def test_sma_invalid_window_too_large_returns_422(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/sma?window=300",
        headers=_auth_header(token),
    )
    assert response.status_code == 422


def test_sma_unsupported_interval_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/sma?interval=1h",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_ema_invalid_ticker_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/AA PL/ema",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_ema_invalid_window_returns_422(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/ema?window=1",
        headers=_auth_header(token),
    )
    assert response.status_code == 422


def test_ema_unsupported_interval_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/ema?interval=1h",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


# --- SMA ---


def test_sma_returns_expected_values(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_history_frame())
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/sma?window=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "SFTESTA"
    assert payload["indicator"] == "sma"
    assert payload["parameters"] == {"window": 2}
    assert payload["provider"] == "yfinance"
    assert payload["cached"] is False

    rows = payload["rows"]
    assert len(rows) == 2
    assert rows[0]["date"] == "2026-01-02"
    assert rows[0]["close"] == 101.0
    assert rows[0]["value"] is None
    assert rows[1]["date"] == "2026-01-03"
    assert rows[1]["close"] == 102.0
    assert rows[1]["value"] == pytest.approx(101.5)


def test_sma_uses_cached_data(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_history_frame())
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        first_resp = client.get(
            "/api/v1/analytics/SFTESTB/sma?window=2",
            headers=_auth_header(token),
        )
    assert first_resp.status_code == 200
    assert first_resp.json()["provider"] == "yfinance"

    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=AssertionError("provider should not be called"),
    ):
        second_resp = client.get(
            "/api/v1/analytics/SFTESTB/sma?window=2",
            headers=_auth_header(token),
        )
    assert second_resp.status_code == 200
    assert second_resp.json()["provider"] == "database"
    assert second_resp.json()["cached"] is True


def test_sma_provider_failure_returns_502(client: TestClient) -> None:
    token = _register_and_login(client)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=RuntimeError("provider down"),
    ):
        response = client.get(
            "/api/v1/analytics/SFTESTA/sma?window=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 502


def test_sma_empty_history_returns_502(client: TestClient) -> None:
    token = _register_and_login(client)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        return_value=FakeTicker(history_frame=pd.DataFrame()),
    ):
        response = client.get(
            "/api/v1/analytics/SFTESTA/sma?window=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 502


def test_sma_insufficient_data_all_null_values(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [102.0],
            "Low": [99.0],
            "Close": [100.0],
            "Volume": [1000],
        },
        index=pd.to_datetime(["2026-01-02"]),
    )
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/sma?window=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["rows"]) == 1
    assert payload["rows"][0]["value"] is None
    assert payload["latest"] is None


def test_sma_refresh_delegates_to_market_data(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_history_frame(close=200.0))
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTC/sma?window=2&refresh=true",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "yfinance"
    assert payload["cached"] is False


def test_sma_latest_returns_last_non_null(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_history_frame())
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/sma?window=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["latest"] is not None
    assert payload["latest"]["date"] == payload["rows"][-1]["date"]
    assert payload["latest"]["value"] == pytest.approx(101.5)


# --- EMA ---


def test_ema_returns_expected_values(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_history_frame())
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/ema?window=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "SFTESTA"
    assert payload["indicator"] == "ema"
    assert payload["parameters"] == {"window": 2}
    assert payload["provider"] == "yfinance"
    assert payload["cached"] is False

    rows = payload["rows"]
    assert len(rows) == 2
    assert rows[0]["date"] == "2026-01-02"
    assert rows[0]["close"] == 101.0
    assert rows[0]["value"] is None
    assert rows[1]["date"] == "2026-01-03"
    assert rows[1]["close"] == 102.0

    expected_ema = 102.0 * 2.0 / 3.0 + 101.0 * 1.0 / 3.0
    assert rows[1]["value"] == pytest.approx(expected_ema)


def test_ema_uses_cached_data(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_history_frame())
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        first_resp = client.get(
            "/api/v1/analytics/SFTESTB/ema?window=2",
            headers=_auth_header(token),
        )
    assert first_resp.status_code == 200
    assert first_resp.json()["provider"] == "yfinance"

    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=AssertionError("provider should not be called"),
    ):
        second_resp = client.get(
            "/api/v1/analytics/SFTESTB/ema?window=2",
            headers=_auth_header(token),
        )
    assert second_resp.status_code == 200
    assert second_resp.json()["provider"] == "database"
    assert second_resp.json()["cached"] is True


def test_ema_provider_failure_returns_502(client: TestClient) -> None:
    token = _register_and_login(client)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=RuntimeError("provider down"),
    ):
        response = client.get(
            "/api/v1/analytics/SFTESTA/ema?window=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 502


def test_ema_empty_history_returns_502(client: TestClient) -> None:
    token = _register_and_login(client)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        return_value=FakeTicker(history_frame=pd.DataFrame()),
    ):
        response = client.get(
            "/api/v1/analytics/SFTESTA/ema?window=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 502


def test_ema_insufficient_data_all_null_values(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [102.0],
            "Low": [99.0],
            "Close": [100.0],
            "Volume": [1000],
        },
        index=pd.to_datetime(["2026-01-02"]),
    )
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/ema?window=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["rows"]) == 1
    assert payload["rows"][0]["value"] is None
    assert payload["latest"] is None


def test_ema_refresh_delegates_to_market_data(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_history_frame(close=200.0))
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTC/ema?window=2&refresh=true",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "yfinance"
    assert payload["cached"] is False


def test_ema_latest_returns_last_non_null(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_history_frame())
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/ema?window=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["latest"] is not None
    assert payload["latest"]["date"] == payload["rows"][-1]["date"]
    expected_ema = 102.0 * 2.0 / 3.0 + 101.0 * 1.0 / 3.0
    assert payload["latest"]["value"] == pytest.approx(expected_ema)


# --- RSI Test Data Helpers ---


def _rsi_frame(
    closes: list[float] | None = None,
) -> pd.DataFrame:
    c = closes if closes is not None else [100.0, 90.0, 110.0, 120.0]
    return pd.DataFrame(
        {
            "Open": c,
            "High": [x + 5.0 for x in c],
            "Low": [x - 5.0 for x in c],
            "Close": c,
            "Volume": [1000] * len(c),
        },
        index=pd.to_datetime(
            ["2026-01-02", "2026-01-03", "2026-01-06", "2026-01-07"][: len(c)],
        ),
    )


def _macd_frame() -> pd.DataFrame:
    closes = [10.0, 20.0, 30.0, 40.0, 50.0]
    return pd.DataFrame(
        {
            "Open": closes,
            "High": [x + 2.0 for x in closes],
            "Low": [x - 2.0 for x in closes],
            "Close": closes,
            "Volume": [1000] * 5,
        },
        index=pd.to_datetime(
            ["2026-01-02", "2026-01-03", "2026-01-06", "2026-01-07", "2026-01-08"],
        ),
    )


# --- RSI Authentication ---


def test_rsi_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/SFTESTA/rsi")
    assert response.status_code == 401


# --- RSI Validation ---


def test_rsi_invalid_ticker_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/AA PL/rsi",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_rsi_invalid_window_small_returns_422(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/rsi?window=1",
        headers=_auth_header(token),
    )
    assert response.status_code == 422


def test_rsi_invalid_window_large_returns_422(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/rsi?window=300",
        headers=_auth_header(token),
    )
    assert response.status_code == 422


def test_rsi_unsupported_interval_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/rsi?interval=1h",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


# --- RSI Expected Values ---


def test_rsi_returns_expected_values(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_rsi_frame())
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/rsi?window=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "SFTESTA"
    assert payload["indicator"] == "rsi"
    assert payload["parameters"] == {"window": 2}

    rows = payload["rows"]
    assert len(rows) == 4
    assert rows[0]["value"] is None
    assert rows[1]["value"] is None
    # avg_gain[2] = (0 + 20)/2 = 10, avg_loss[2] = (10 + 0)/2 = 5
    # rs[2] = 2, rsi[2] = 100 - 100/3 = 66.666...
    assert rows[2]["value"] == pytest.approx(100.0 - 100.0 / 3.0)
    # avg_gain[3] = (10*1+10)/2 = 10, avg_loss[3] = (5*1+0)/2 = 2.5
    # rs[3] = 4, rsi[3] = 100 - 100/5 = 80
    assert rows[3]["value"] == pytest.approx(80.0)


def test_rsi_flat_prices_returns_50(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _rsi_frame(closes=[100.0, 100.0, 100.0, 100.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/rsi?window=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    rows = response.json()["rows"]
    # All changes are 0, so avg_gain=avg_loss=0 -> RSI=50
    assert rows[2]["value"] == pytest.approx(50.0)
    assert rows[3]["value"] == pytest.approx(50.0)


def test_rsi_all_gains_returns_100(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _rsi_frame(closes=[100.0, 110.0, 120.0, 130.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/rsi?window=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    rows = response.json()["rows"]
    # All gains, no losses -> RSI=100
    assert rows[2]["value"] == pytest.approx(100.0)
    assert rows[3]["value"] == pytest.approx(100.0)


def test_rsi_all_losses_returns_0(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _rsi_frame(closes=[100.0, 90.0, 80.0, 70.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/rsi?window=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    rows = response.json()["rows"]
    # All losses, no gains -> RSI=0
    assert rows[2]["value"] == pytest.approx(0.0)
    assert rows[3]["value"] == pytest.approx(0.0)


# --- RSI Cache & Provider ---


def test_rsi_uses_cached_data(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_rsi_frame())
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        first_resp = client.get(
            "/api/v1/analytics/SFTESTB/rsi?window=2",
            headers=_auth_header(token),
        )
    assert first_resp.status_code == 200
    assert first_resp.json()["provider"] == "yfinance"

    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=AssertionError("provider should not be called"),
    ):
        second_resp = client.get(
            "/api/v1/analytics/SFTESTB/rsi?window=2",
            headers=_auth_header(token),
        )
    assert second_resp.status_code == 200
    assert second_resp.json()["provider"] == "database"
    assert second_resp.json()["cached"] is True


def test_rsi_provider_failure_returns_502(client: TestClient) -> None:
    token = _register_and_login(client)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=RuntimeError("provider down"),
    ):
        response = client.get(
            "/api/v1/analytics/SFTESTA/rsi?window=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 502


def test_rsi_empty_history_returns_502(client: TestClient) -> None:
    token = _register_and_login(client)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        return_value=FakeTicker(history_frame=pd.DataFrame()),
    ):
        response = client.get(
            "/api/v1/analytics/SFTESTA/rsi?window=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 502


# --- RSI Warmup & Latest ---


def test_rsi_insufficient_data_returns_all_null(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _rsi_frame(closes=[100.0, 110.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/rsi?window=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["rows"]) == 2
    assert payload["rows"][0]["value"] is None
    assert payload["rows"][1]["value"] is None
    assert payload["latest"] is None


def test_rsi_refresh_delegates_to_market_data(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_rsi_frame(closes=[200.0, 210.0, 220.0, 230.0]))
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTC/rsi?window=2&refresh=true",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "yfinance"
    assert payload["cached"] is False


def test_rsi_latest_returns_last_non_null(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_rsi_frame())
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/rsi?window=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["latest"] is not None
    assert payload["latest"]["date"] == payload["rows"][-1]["date"]
    assert payload["latest"]["value"] == pytest.approx(80.0)


# --- MACD Authentication ---


def test_macd_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/analytics/SFTESTA/macd")
    assert response.status_code == 401


# --- MACD Validation ---


def test_macd_invalid_ticker_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/AA PL/macd",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_macd_invalid_fast_returns_422(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/macd?fast=1",
        headers=_auth_header(token),
    )
    assert response.status_code == 422


def test_macd_invalid_slow_returns_422(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/macd?slow=1",
        headers=_auth_header(token),
    )
    assert response.status_code == 422


def test_macd_invalid_signal_returns_422(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/macd?signal=1",
        headers=_auth_header(token),
    )
    assert response.status_code == 422


def test_macd_slow_not_greater_than_fast_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/macd?fast=26&slow=12",
        headers=_auth_header(token),
    )
    assert response.status_code == 400
    assert "greater than" in response.json()["detail"]


def test_macd_equal_fast_slow_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/macd?fast=12&slow=12",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_macd_unsupported_interval_returns_400(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(
        "/api/v1/analytics/SFTESTA/macd?interval=1h",
        headers=_auth_header(token),
    )
    assert response.status_code == 400


# --- MACD Expected Values ---


def test_macd_returns_expected_values(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_macd_frame())
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/macd?fast=2&slow=3&signal=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "SFTESTA"
    assert payload["indicator"] == "macd"
    assert payload["parameters"] == {"fast": 2, "slow": 3, "signal": 2}

    rows = payload["rows"]
    assert len(rows) == 5

    # Row 0 (index 0): all null (warmup)
    assert rows[0]["macd"] is None
    assert rows[0]["signal"] is None
    assert rows[0]["histogram"] is None

    # Row 1 (index 1): ema_slow still NaN -> macd NaN
    assert rows[1]["macd"] is None

    # Row 2 (index 2): first non-NaN macd (slow-1=2), signal still NaN
    assert rows[2]["macd"] is not None
    assert rows[2]["signal"] is None
    assert rows[2]["histogram"] is None

    # Row 3 (index 3): first non-NaN signal (slow+signal-2=3), histogram non-NaN
    assert rows[3]["macd"] is not None
    assert rows[3]["signal"] is not None
    assert rows[3]["histogram"] is not None

    # Row 4: all non-null
    assert rows[4]["macd"] is not None
    assert rows[4]["signal"] is not None
    assert rows[4]["histogram"] is not None

    # Verify values using pandas reference
    closes = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
    ref_fast = closes.ewm(span=2, adjust=False, min_periods=2).mean()
    ref_slow = closes.ewm(span=3, adjust=False, min_periods=3).mean()
    ref_macd = ref_fast - ref_slow
    ref_signal = ref_macd.ewm(span=2, adjust=False, min_periods=2).mean()
    ref_histogram = ref_macd - ref_signal

    assert rows[2]["macd"] == pytest.approx(float(ref_macd.iloc[2]))
    assert rows[3]["macd"] == pytest.approx(float(ref_macd.iloc[3]))
    assert rows[3]["signal"] == pytest.approx(float(ref_signal.iloc[3]))
    assert rows[3]["histogram"] == pytest.approx(float(ref_histogram.iloc[3]))


# --- MACD Cache & Provider ---


def test_macd_uses_cached_data(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_macd_frame())
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        first_resp = client.get(
            "/api/v1/analytics/SFTESTB/macd?fast=2&slow=3&signal=2",
            headers=_auth_header(token),
        )
    assert first_resp.status_code == 200
    assert first_resp.json()["provider"] == "yfinance"

    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=AssertionError("provider should not be called"),
    ):
        second_resp = client.get(
            "/api/v1/analytics/SFTESTB/macd?fast=2&slow=3&signal=2",
            headers=_auth_header(token),
        )
    assert second_resp.status_code == 200
    assert second_resp.json()["provider"] == "database"
    assert second_resp.json()["cached"] is True


def test_macd_provider_failure_returns_502(client: TestClient) -> None:
    token = _register_and_login(client)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=RuntimeError("provider down"),
    ):
        response = client.get(
            "/api/v1/analytics/SFTESTA/macd",
            headers=_auth_header(token),
        )
    assert response.status_code == 502


def test_macd_empty_history_returns_502(client: TestClient) -> None:
    token = _register_and_login(client)
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        return_value=FakeTicker(history_frame=pd.DataFrame()),
    ):
        response = client.get(
            "/api/v1/analytics/SFTESTA/macd",
            headers=_auth_header(token),
        )
    assert response.status_code == 502


# --- MACD Warmup & Latest ---


def test_macd_insufficient_data_returns_all_null(client: TestClient) -> None:
    token = _register_and_login(client)
    closes = [10.0, 20.0, 30.0]
    frame = pd.DataFrame(
        {
            "Open": closes,
            "High": [x + 2 for x in closes],
            "Low": [x - 2 for x in closes],
            "Close": closes,
            "Volume": [1000] * 3,
        },
        index=pd.to_datetime(["2026-01-02", "2026-01-03", "2026-01-06"]),
    )
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/macd?fast=12&slow=26&signal=9",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    payload = response.json()
    assert all(r["macd"] is None for r in payload["rows"])
    assert all(r["signal"] is None for r in payload["rows"])
    assert all(r["histogram"] is None for r in payload["rows"])
    assert payload["latest"] is None


def test_macd_refresh_delegates_to_market_data(client: TestClient) -> None:
    token = _register_and_login(client)
    frame = _macd_frame()
    frame.iloc[-1, frame.columns.get_loc("Close")] = 200.0
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTC/macd?fast=2&slow=3&signal=2&refresh=true",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "yfinance"
    assert payload["cached"] is False


def test_macd_latest_returns_last_complete_point(client: TestClient) -> None:
    token = _register_and_login(client)
    fake = FakeTicker(history_frame=_macd_frame())
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/analytics/SFTESTA/macd?fast=2&slow=3&signal=2",
            headers=_auth_header(token),
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["latest"] is not None
    assert payload["latest"]["date"] == payload["rows"][-1]["date"]
    assert payload["latest"]["macd"] is not None
    assert payload["latest"]["signal"] is not None
    assert payload["latest"]["histogram"] is not None
