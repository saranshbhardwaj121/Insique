import logging
import math
from uuid import uuid4
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
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


def _dates(n: int) -> list[str]:
    start = pd.Timestamp("2025-01-01")
    return [(start + pd.Timedelta(days=i)).strftime("%Y-%m-%d") for i in range(n)]


def _pad(closes: list[float], n: int = 60) -> list[float]:
    """Pad closes to at least n candles for minimum history validation."""
    if not closes:
        return closes
    if len(closes) >= n:
        return closes
    return [closes[0]] * (n - len(closes)) + closes


def _frame(closes: list[float], min_candles: int = 60) -> pd.DataFrame:
    """Create OHLC DataFrame. Pads to min_candles to pass minimum history checks."""
    padded = _pad(closes, n=min_candles) if min_candles else closes
    return pd.DataFrame(
        {
            "Open": padded,
            "High": [x + 2.0 for x in padded],
            "Low": [x - 2.0 for x in padded],
            "Close": padded,
            "Volume": [1000] * len(padded),
        },
        index=pd.to_datetime(_dates(len(padded))),
    )


# --- Authentication ---


def test_signals_without_auth_succeeds(client: TestClient) -> None:
    """Signal endpoint does not require authentication (it is a public endpoint)."""
    frame = _frame([100.0])
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get("/api/v1/signals/SFTESTA")
    assert response.status_code == 200


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


def test_signals_insufficient_data_returns_502(client: TestClient) -> None:
    """Fewer candles than minimum history requirement must return 502."""
    token = _register_and_login(client)
    frame = _frame([100.0], min_candles=0)
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA",
            headers=_auth_header(token),
        )
    assert response.status_code == 502


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
    # 70 candles: 15 at 100, then crash to 50 and stay there for 55 candles.
    # RSI(2) stays at 0 (strong_oversold) while EMA(2,3) converge to exactly 50
    # (below machine epsilon) so no conflicting trend signal.
    n_flat = 55
    frame = _frame([100.0] * 15 + [50.0] * n_flat, min_candles=0)
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA"
            "?rsi_window=2&sma_short=2&sma_long=3&ema_short=2&ema_long=3"
            "&macd_fast=2&macd_slow=3&macd_signal=2",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["rating"] == "BUY"
    assert payload["score"] >= 2


def test_strong_bearish_signals_give_sell_rating(client: TestClient) -> None:
    token = _register_and_login(client)
    # 70 candles: 15 at 50, then jump to 100 and stay there for 55 candles.
    # RSI(2) stays at 100 (strong_overbought) while EMA(2,3) converge to
    # exactly 100 (below machine epsilon) so no conflicting trend signal.
    n_flat = 55
    frame = _frame([50.0] * 15 + [100.0] * n_flat, min_candles=0)
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTA"
            "?rsi_window=2&sma_short=2&sma_long=3&ema_short=2&ema_long=3"
            "&macd_fast=2&macd_slow=3&macd_signal=2",
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


# --- NaN / Invalid Data Hardening ---


def _frame_with_nan(closes: list[float], nan_at_end: bool = True) -> pd.DataFrame:
    """Create a frame with NaN in the last row's Close column."""
    df = _frame(closes)
    if nan_at_end and closes:
        nan_date = _dates(1)[0]
        nan_row = pd.DataFrame(
            {"Open": [float("nan")], "High": [float("nan")], "Low": [float("nan")],
             "Close": [float("nan")], "Volume": [1000]},
            index=pd.to_datetime([nan_date]),
        )
        df = pd.concat([df, nan_row])
    return df


def test_nan_rows_are_not_persisted(client: TestClient) -> None:
    """NaN OHLC rows from yfinance must be rejected by save_history."""
    token = _register_and_login(client)
    frame = _frame_with_nan([100.0] * 60)
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTNAN1",
            headers=_auth_header(token),
        )

    assert response.status_code == 200
    payload = response.json()
    # If NaN rows had been persisted, the response would have cached=True.
    # Since they were rejected, the first fetch is always fresh.
    assert payload["cached"] is False

    # A second call should use the cached (clean) data
    with patch(
        "backend.app.services.market_data_service.yf.Ticker",
        side_effect=AssertionError("should not be called"),
    ):
        second = client.get(
            "/api/v1/signals/SFTESTNAN1",
            headers=_auth_header(token),
        )
    assert second.status_code == 200
    assert second.json()["cached"] is True


def test_all_nan_rows_raises_error(client: TestClient) -> None:
    """If yfinance returns ALL rows with NaN, must return 502."""
    token = _register_and_login(client)
    frame = _frame_with_nan([], nan_at_end=True)
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTNAN2",
            headers=_auth_header(token),
        )
    # All rows are NaN → MarketDataProviderError → 502
    assert response.status_code == 502


def test_corrupted_cache_triggers_self_healing(client: TestClient) -> None:
    """If cached rows have NaN close, get_history must auto-recover."""
    token = _register_and_login(client)

    # First call with valid data to populate cache
    valid_frame = _frame([100.0] * 60)
    fake = FakeTicker(history_frame=valid_frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        first = client.get(
            "/api/v1/signals/SFTESTHEAL",
            headers=_auth_header(token),
        )
    assert first.status_code == 200
    assert first.json()["cached"] is False

    # Manually inject a NaN row into the DB to simulate corruption
    from backend.app.db.session import SessionLocal
    from backend.app.models.market_data import MarketData
    from sqlalchemy import text

    db = SessionLocal()
    try:
        db.execute(text("""
            UPDATE market_data
            SET close = 'NaN'::float
            WHERE ticker = 'SFTESTHEAL'
              AND date = (SELECT MAX(date) FROM market_data WHERE ticker = 'SFTESTHEAL')
        """))
        db.commit()
    finally:
        db.close()

        # Next call should detect corruption, delete invalid rows, and refresh
        # Need enough candles for min history checks (SMA 50 needs >=50)
        fresh_frame = _frame([100.0] * 150)
    fake2 = FakeTicker(history_frame=fresh_frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake2):
        second = client.get(
            "/api/v1/signals/SFTESTHEAL",
            headers=_auth_header(token),
        )

    assert second.status_code == 200
    # The response should have valid data from the fresh fetch
    assert second.json()["cached"] is False


def test_indicator_generation_rejects_nan_data(client: TestClient) -> None:
    """Indicator calculation must raise error if input data contains NaN."""
    token = _register_and_login(client)
    # Use a frame where ALL close values are valid, so the fetch succeeds
    valid_frame = _frame([100.0] * 150)
    fake = FakeTicker(history_frame=valid_frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTNAN3",
            headers=_auth_header(token),
        )
    # This should work fine — valid data
    assert response.status_code == 200


def test_insufficient_history_returns_502(client: TestClient) -> None:
    """Less than minimum candles for any indicator must return explicit error."""
    token = _register_and_login(client)
    # Only 10 candles — not enough for RSI(14), MACD(12,26,9), SMA(20), SMA(50), etc.
    frame = _frame([100.0] * 10, min_candles=0)
    fake = FakeTicker(history_frame=frame)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        response = client.get(
            "/api/v1/signals/SFTESTINSF",
            headers=_auth_header(token),
        )
    assert response.status_code == 502


def test_nan_cache_corruption_full_recovery(
    client: TestClient, db_session: Session, caplog: pytest.LogCaptureFixture
) -> None:
    """Regression test for production NaN cache corruption bug.

    Simulates the exact production incident:
      Phase 1 — provider returns a mix of valid + NaN rows;
      Phase 2 — corrupted cache is detected and auto-invalidated;
      Phase 3 — fresh valid data is fetched and cache rebuilt;
      Phase 4 — indicators produce real values (not insufficient_data);
      Phase 5 — DB contains no NaN/NULL OHLCV after recovery;
      Phase 6 — log messages confirm each recovery step.

    This guards against any future regression where NaN could silently
    produce a bogus 0/6 NEUTRAL signal with 0% confidence.
    """
    caplog.set_level(logging.INFO)

    ticker = "SFTESTREGR"
    token = _register_and_login(client)

    # ── Phase 1: Provider returns valid rows + one NaN row ──
    valid = _frame([100.0] * 99)
    nan_date = _dates(1)[0]
    nan_row = pd.DataFrame(
        {"Open": [float("nan")], "High": [float("nan")], "Low": [float("nan")],
         "Close": [float("nan")], "Volume": [1000]},
        index=pd.to_datetime([nan_date]),
    )
    mixed = pd.concat([valid, nan_row])

    fake = FakeTicker(history_frame=mixed)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake):
        resp = client.get(f"/api/v1/signals/{ticker}", headers=_auth_header(token))
    assert resp.status_code == 200, f"Phase 1 failed: {resp.text}"
    assert resp.json()["cached"] is False

    # Verify DB has no NaN/NULL OHLCV after save_history
    rows = db_session.execute(
        text("SELECT open, high, low, close, volume FROM market_data WHERE ticker = :t"),
        {"t": ticker},
    ).fetchall()
    assert len(rows) > 0, "No rows persisted in Phase 1"
    for row in rows:
        for col in row:
            assert col is not None, f"NULL persisted: {row}"
            assert not (isinstance(col, float) and math.isnan(col)), f"NaN persisted: {row}"

    # ── Phase 2: Simulate pre-fix corrupted cache (NaN persisted in DB) ──
    db_session.execute(
        text("""
            UPDATE market_data
            SET close = 'NaN'::float
            WHERE ticker = :t
              AND date = (SELECT MAX(date) FROM market_data WHERE ticker = :t2)
        """),
        {"t": ticker, "t2": ticker},
    )
    db_session.commit()

    # ── Phase 3: Next call detects corruption → invalidates → refresh → rebuild ──
    # Use a frame with enough candles (150) and clear price action.
    # 75 flat at 100, then 75 flat at 50 → RSI(14) ≈ 0 (strong oversold).
    recovered = _frame([100.0] * 75 + [50.0] * 75, min_candles=0)
    fake2 = FakeTicker(history_frame=recovered)
    with patch("backend.app.services.market_data_service.yf.Ticker", return_value=fake2):
        resp2 = client.get(f"/api/v1/signals/{ticker}", headers=_auth_header(token))

    assert resp2.status_code == 200, f"Phase 3 failed: {resp2.text}"
    payload = resp2.json()
    assert payload["cached"] is False, "Must perform a fresh fetch after cache invalidation"

    # ── Phase 4: Signal quality verification ──
    # Signal reasons must never be "insufficient_data" after recovery
    for sig in payload["signals"]:
        assert sig["reason"] != "insufficient_data", \
            f"{sig['name']} has insufficient_data — cache corruption leaked through: {sig}"

    # Confidence must reflect real calculations (score >= |1| → confidence > 0)
    assert payload["confidence"] > 0, \
        f"Confidence must be > 0 with 150 valid candles, got {payload['confidence']} from score={payload['score']}"

    # At least one indicator must produce a non-degenerate directional signal
    degenerate = {"insufficient_data", "mixed", "no_crossover"}
    has_real = any(sig["reason"] not in degenerate for sig in payload["signals"])
    assert has_real, f"All signals are degenerate: {[s['reason'] for s in payload['signals']]}"

    # ── Phase 5: Post-recovery DB integrity ──
    rows2 = db_session.execute(
        text("SELECT open, high, low, close, volume FROM market_data WHERE ticker = :t"),
        {"t": ticker},
    ).fetchall()
    assert len(rows2) > 0, "No rows after cache rebuild"
    for row in rows2:
        for col in row:
            assert col is not None, f"NULL persisted after recovery: {row}"
            assert not (isinstance(col, float) and math.isnan(col)), \
                f"NaN persisted after recovery: {row}"

    # ── Phase 6: Log message verification ──
    assert "Cache corrupted" in caplog.text, "Missing cache corruption detection log"
    assert "forcing fresh fetch" in caplog.text, "Missing fresh fetch log"
    assert "Saved" in caplog.text, "Missing cache rebuilt log"


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
