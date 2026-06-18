import pandas as pd
from sqlalchemy.orm import Session

from backend.app.schemas.analytics import IndicatorPoint, IndicatorResponse, MacdPoint, MacdResponse
from backend.app.schemas.market_data import HistoricalBarRead
from backend.app.services.market_data_service import (
    MarketDataProviderError,
    MarketDataService,
    MarketDataValidationError,
)


class AnalyticsService:
    MIN_WINDOW = 2
    MAX_WINDOW = 250

    def __init__(self, session: Session) -> None:
        self.session = session
        self.market_data_service = MarketDataService(session)

    def _compute_indicator_rows(
        self,
        rows: list[HistoricalBarRead],
        indicator: str,
        window: int,
    ) -> tuple[list[IndicatorPoint], IndicatorPoint | None]:
        df = pd.DataFrame(
            [{"date": r.date, "close": float(r.close)} for r in rows],
        )
        df = df.sort_values("date").reset_index(drop=True)

        if indicator == "sma":
            series = df["close"].rolling(window=window, min_periods=window).mean()
        elif indicator == "ema":
            series = df["close"].ewm(span=window, adjust=False, min_periods=window).mean()
        else:
            raise ValueError(f"Unknown indicator: {indicator}")

        indicator_rows = [
            IndicatorPoint(
                date=r["date"],
                close=float(r["close"]),
                value=float(v) if pd.notna(v) else None,
            )
            for r, v in zip(df.to_dict("records"), series)
        ]

        latest = None
        for r in reversed(indicator_rows):
            if r.value is not None:
                latest = r
                break

        return indicator_rows, latest

    def _compute_rsi_rows(
        self,
        rows: list[HistoricalBarRead],
        window: int,
    ) -> tuple[list[IndicatorPoint], IndicatorPoint | None]:
        df = pd.DataFrame(
            [{"date": r.date, "close": float(r.close)} for r in rows],
        )
        df = df.sort_values("date").reset_index(drop=True)
        close = df["close"]
        n = len(close)

        if window >= n:
            indicator_rows = [
                IndicatorPoint(date=r["date"], close=float(r["close"]), value=None)
                for _, r in df.iterrows()
            ]
            return indicator_rows, None

        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)

        avg_gain = pd.Series(0.0, index=close.index)
        avg_loss = pd.Series(0.0, index=close.index)

        avg_gain.iloc[window] = gain.iloc[1 : window + 1].mean()
        avg_loss.iloc[window] = loss.iloc[1 : window + 1].mean()

        for i in range(window + 1, n):
            avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (window - 1) + gain.iloc[i]) / window
            avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (window - 1) + loss.iloc[i]) / window

        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))

        no_loss = (avg_gain > 0) & (avg_loss == 0)
        no_gain = (avg_gain == 0) & (avg_loss > 0)
        no_change = (avg_gain == 0) & (avg_loss == 0)

        rsi[no_loss] = 100.0
        rsi[no_gain] = 0.0
        rsi[no_change] = 50.0

        rsi.iloc[:window] = None

        indicator_rows = [
            IndicatorPoint(
                date=r["date"],
                close=float(r["close"]),
                value=float(rsi.iloc[i]) if pd.notna(rsi.iloc[i]) else None,
            )
            for i, (_, r) in enumerate(df.iterrows())
        ]

        latest = None
        for r in reversed(indicator_rows):
            if r.value is not None:
                latest = r
                break

        return indicator_rows, latest

    def _compute_macd_rows(
        self,
        rows: list[HistoricalBarRead],
        fast: int,
        slow: int,
        signal: int,
    ) -> tuple[list[MacdPoint], MacdPoint | None]:
        df = pd.DataFrame(
            [{"date": r.date, "close": float(r.close)} for r in rows],
        )
        df = df.sort_values("date").reset_index(drop=True)
        close = df["close"]

        ema_fast = close.ewm(span=fast, adjust=False, min_periods=fast).mean()
        ema_slow = close.ewm(span=slow, adjust=False, min_periods=slow).mean()
        macd_line = ema_fast - ema_slow

        signal_line = macd_line.ewm(span=signal, adjust=False, min_periods=signal).mean()
        histogram = macd_line - signal_line

        macd_points = [
            MacdPoint(
                date=r["date"],
                close=float(r["close"]),
                macd=float(macd_line.iloc[i]) if pd.notna(macd_line.iloc[i]) else None,
                signal=float(signal_line.iloc[i]) if pd.notna(signal_line.iloc[i]) else None,
                histogram=float(histogram.iloc[i]) if pd.notna(histogram.iloc[i]) else None,
            )
            for i, (_, r) in enumerate(df.iterrows())
        ]

        latest = None
        for mp in reversed(macd_points):
            if mp.macd is not None and mp.signal is not None and mp.histogram is not None:
                latest = mp
                break

        return macd_points, latest

    def get_sma(
        self,
        ticker: str,
        window: int,
        period: str = "6mo",
        interval: str = "1d",
        refresh: bool = False,
    ) -> IndicatorResponse:
        history = self.market_data_service.get_history(ticker, period, interval, refresh)
        if not history.rows:
            raise MarketDataProviderError("No historical data available for calculation")
        rows, latest = self._compute_indicator_rows(history.rows, "sma", window)
        return IndicatorResponse(
            ticker=history.ticker,
            indicator="sma",
            period=period,
            interval=interval,
            parameters={"window": window},
            rows=rows,
            latest=latest,
            provider=history.provider,
            cached=history.cached,
            fetched_at=history.fetched_at,
        )

    def get_ema(
        self,
        ticker: str,
        window: int,
        period: str = "6mo",
        interval: str = "1d",
        refresh: bool = False,
    ) -> IndicatorResponse:
        history = self.market_data_service.get_history(ticker, period, interval, refresh)
        if not history.rows:
            raise MarketDataProviderError("No historical data available for calculation")
        rows, latest = self._compute_indicator_rows(history.rows, "ema", window)
        return IndicatorResponse(
            ticker=history.ticker,
            indicator="ema",
            period=period,
            interval=interval,
            parameters={"window": window},
            rows=rows,
            latest=latest,
            provider=history.provider,
            cached=history.cached,
            fetched_at=history.fetched_at,
        )

    def get_rsi(
        self,
        ticker: str,
        window: int = 14,
        period: str = "6mo",
        interval: str = "1d",
        refresh: bool = False,
    ) -> IndicatorResponse:
        history = self.market_data_service.get_history(ticker, period, interval, refresh)
        if not history.rows:
            raise MarketDataProviderError("No historical data available for calculation")
        rows, latest = self._compute_rsi_rows(history.rows, window)
        return IndicatorResponse(
            ticker=history.ticker,
            indicator="rsi",
            period=period,
            interval=interval,
            parameters={"window": window},
            rows=rows,
            latest=latest,
            provider=history.provider,
            cached=history.cached,
            fetched_at=history.fetched_at,
        )

    def get_macd(
        self,
        ticker: str,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
        period: str = "6mo",
        interval: str = "1d",
        refresh: bool = False,
    ) -> MacdResponse:
        if slow <= fast:
            raise MarketDataValidationError("Slow period must be greater than fast period")
        history = self.market_data_service.get_history(ticker, period, interval, refresh)
        if not history.rows:
            raise MarketDataProviderError("No historical data available for calculation")
        rows, latest = self._compute_macd_rows(history.rows, fast, slow, signal)
        return MacdResponse(
            ticker=history.ticker,
            indicator="macd",
            period=period,
            interval=interval,
            parameters={"fast": fast, "slow": slow, "signal": signal},
            rows=rows,
            latest=latest,
            provider=history.provider,
            cached=history.cached,
            fetched_at=history.fetched_at,
        )
