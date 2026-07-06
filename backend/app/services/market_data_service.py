import logging
import math
import re
from collections.abc import Iterable
from datetime import date, datetime, timedelta, timezone
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session
import yfinance as yf

from backend.app.core.config import get_settings
from backend.app.models.market_data import MarketData
from backend.app.repositories.market_data_repository import MarketDataRepository
from backend.app.schemas.market_data import HistoricalBarRead, HistoricalDataResponse, QuoteRead
from backend.app.services.cache import quote_cache

logger = logging.getLogger(__name__)


class MarketDataValidationError(ValueError):
    pass


class MarketDataProviderError(RuntimeError):
    pass


class MarketDataService:
    SUPPORTED_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
    SUPPORTED_INTERVALS = {"1d"}
    TICKER_PATTERN = re.compile(r"^[A-Z0-9.^-]+$")

    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.repository = MarketDataRepository(session)

    def normalize_ticker(self, ticker: str) -> str:
        normalized = ticker.strip().upper()
        if not normalized:
            raise MarketDataValidationError("Ticker cannot be empty")
        if len(normalized) > 20:
            raise MarketDataValidationError("Ticker cannot exceed 20 characters")
        if not self.TICKER_PATTERN.fullmatch(normalized):
            raise MarketDataValidationError("Ticker contains unsupported characters")
        return normalized

    def get_quote(self, ticker: str) -> QuoteRead:
        normalized = self.normalize_ticker(ticker)
        cached = quote_cache.get(normalized)
        if cached is not None:
            return cached
        fetched_at = datetime.now(timezone.utc)
        try:
            provider_ticker = yf.Ticker(normalized)
            fast_info = provider_ticker.fast_info
            info = getattr(provider_ticker, "info", {}) or {}
        except Exception as exc:  # noqa: BLE001
            raise MarketDataProviderError("Unable to fetch quote from provider") from exc

        price = self._read_float(fast_info, "last_price", "lastPrice")
        if price is None:
            price = self._read_float(info, "regularMarketPrice", "currentPrice")

        result = QuoteRead(
            ticker=normalized,
            name=self._read_str(info, "shortName", "longName"),
            currency=self._read_str(fast_info, "currency") or self._read_str(info, "currency"),
            price=price,
            previous_close=self._read_float(fast_info, "previous_close", "previousClose")
            or self._read_float(info, "previousClose", "regularMarketPreviousClose"),
            open=self._read_float(fast_info, "open") or self._read_float(info, "regularMarketOpen"),
            day_high=self._read_float(fast_info, "day_high", "dayHigh")
            or self._read_float(info, "dayHigh", "regularMarketDayHigh"),
            day_low=self._read_float(fast_info, "day_low", "dayLow")
            or self._read_float(info, "dayLow", "regularMarketDayLow"),
            volume=self._read_int(fast_info, "last_volume", "lastVolume")
            or self._read_int(info, "volume", "regularMarketVolume"),
            market_cap=self._read_int(fast_info, "market_cap", "marketCap")
            or self._read_int(info, "marketCap"),
            exchange=self._read_str(fast_info, "exchange") or self._read_str(info, "exchange"),
            provider="yfinance",
            fetched_at=fetched_at,
        )
        quote_cache.set(normalized, result)
        return result

    def get_history(
        self,
        ticker: str,
        period: str = "1mo",
        interval: str = "1d",
        refresh: bool = False,
    ) -> HistoricalDataResponse:
        normalized = self.normalize_ticker(ticker)
        if period not in self.SUPPORTED_PERIODS:
            raise MarketDataValidationError("Unsupported history period")
        if interval not in self.SUPPORTED_INTERVALS:
            raise MarketDataValidationError("Unsupported history interval")

        fetched_at = datetime.now(timezone.utc)
        cached_rows = self.repository.list_by_ticker(normalized)

        # Self-healing: validate cached rows for NaN/Inf
        cache_invalidated = False
        if cached_rows:
            invalid_rows = [r for r in cached_rows if not self._is_valid_ohlcv(r)]
            if invalid_rows:
                dates = [str(r.date) for r in invalid_rows[:5]]
                logger.warning("Cache corrupted for %s: %d invalid rows (dates: %s). Deleting and forcing refresh.",
                               normalized, len(invalid_rows), ", ".join(dates))
                deleted = self.repository.delete_by_ticker(normalized)
                self.session.commit()
                cache_invalidated = True
                cached_rows = []
                logger.info("Deleted %d corrupted rows for %s, forcing fresh fetch", deleted, normalized)

        # Return fresh cache if valid and recent
        if cached_rows and not refresh and not cache_invalidated and self._cache_is_fresh(normalized):
            logger.info("Cache hit for %s (%d rows, period=%s)", normalized, len(cached_rows), period)
            return HistoricalDataResponse(
                ticker=normalized,
                period=period,
                interval=interval,
                rows=self._to_history_rows(cached_rows),
                provider="database",
                cached=True,
                fetched_at=fetched_at,
            )

        logger.info("Cache miss for %s (refresh=%s, cache_invalidated=%s). Fetching from yfinance.",
                    normalized, refresh, cache_invalidated)
        frame = self._fetch_history_from_yfinance(normalized, period, interval)
        saved_count = self.save_history(normalized, frame)
        if saved_count == 0:
            raise MarketDataProviderError("Provider returned no historical data")

        rows = self.repository.list_by_ticker(normalized)
        provider = "database" if cache_invalidated else "yfinance"
        return HistoricalDataResponse(
            ticker=normalized,
            period=period,
            interval=interval,
            rows=self._to_history_rows(rows),
            provider=provider,
            cached=False,
            fetched_at=fetched_at,
        )

    def save_history(self, ticker: str, frame: pd.DataFrame) -> int:
        ticker = self.normalize_ticker(ticker)
        rows: list[MarketData] = []
        skipped = 0
        for index, row in frame.iterrows():
            row_date = index.date() if hasattr(index, "date") else index
            parsed_date = row_date if isinstance(row_date, date) else row_date.to_pydatetime().date()

            row_data = MarketData(
                ticker=ticker,
                date=parsed_date,
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(row["Volume"]),
            )

            if not self._is_valid_ohlcv(row_data):
                logger.warning("Skipping row with invalid OHLCV: %s %s (open=%s, high=%s, low=%s, close=%s, volume=%s)",
                               ticker, parsed_date, row_data.open, row_data.high,
                               row_data.low, row_data.close, row_data.volume)
                skipped += 1
                continue

            rows.append(row_data)

        if skipped and not rows:
            logger.error("All %d rows from yfinance for %s contain invalid OHLCV — provider returned incomplete data",
                         skipped, ticker)
            raise MarketDataProviderError("Provider returned incomplete historical data (all rows contain invalid OHLCV)")

        if rows:
            self.repository.upsert_rows(rows)
            self.session.commit()

        if skipped:
            logger.info("Saved %d rows for %s, skipped %d rows with invalid OHLCV", len(rows), ticker, skipped)

        return len(rows)

    def list_cached_ticker(self, ticker: str) -> Iterable[MarketData]:
        normalized = self.normalize_ticker(ticker)
        return self.repository.list_by_ticker(normalized)

    def _fetch_history_from_yfinance(
        self, ticker: str, period: str, interval: str
    ) -> pd.DataFrame:
        try:
            frame = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=False)
        except Exception as exc:  # noqa: BLE001
            raise MarketDataProviderError("Unable to fetch history from provider") from exc
        if frame.empty:
            raise MarketDataProviderError("Provider returned no historical data")
        return frame

    def _cache_is_fresh(self, ticker: str) -> bool:
        latest_updated_at = self.repository.get_latest_updated_at(ticker)
        if latest_updated_at is None:
            return False
        if latest_updated_at.tzinfo is None:
            latest_updated_at = latest_updated_at.replace(tzinfo=timezone.utc)
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.settings.market_data_cache_days)
        return latest_updated_at >= cutoff

    def _is_valid_ohlcv(self, row: MarketData) -> bool:
        for val in (row.open, row.high, row.low, row.close):
            if val is None or math.isnan(val) or math.isinf(val):
                return False
        if row.volume is None or math.isnan(float(row.volume)) or math.isinf(float(row.volume)):
            return False
        return True

    def _to_history_rows(self, rows: Iterable[MarketData]) -> list[HistoricalBarRead]:
        return [
            HistoricalBarRead(
                date=row.date,
                open=float(row.open),
                high=float(row.high),
                low=float(row.low),
                close=float(row.close),
                volume=int(row.volume),
            )
            for row in rows
        ]

    def _read_value(self, source: Any, *keys: str) -> Any:
        for key in keys:
            try:
                if isinstance(source, dict) and key in source:
                    return source[key]
                value = getattr(source, key)
                if value is not None:
                    return value
            except Exception:  # noqa: BLE001
                continue
        return None

    def _read_float(self, source: Any, *keys: str) -> float | None:
        value = self._read_value(source, *keys)
        if value is None:
            return None
        number = float(value)
        return None if math.isnan(number) else number

    def _read_int(self, source: Any, *keys: str) -> int | None:
        value = self._read_value(source, *keys)
        if value is None:
            return None
        return int(value)

    def _read_str(self, source: Any, *keys: str) -> str | None:
        value = self._read_value(source, *keys)
        return str(value) if value is not None else None
