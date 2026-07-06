import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.schemas.analytics import IndicatorPoint, MacdPoint
from backend.app.schemas.market_data import HistoricalBarRead
from backend.app.schemas.signals import SignalDetail, SignalSummaryResponse
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.market_data_service import (
    MarketDataProviderError,
    MarketDataService,
    MarketDataValidationError,
)

logger = logging.getLogger(__name__)

MAX_ABS_SCORE = 6


def _compute_confidence(score: int) -> float:
    return min(abs(score) / MAX_ABS_SCORE, 1.0)


def _aggregate_rating(signals: list[SignalDetail]) -> tuple[str, int]:
    total = sum(s.score for s in signals)
    if total >= 2:
        return "BUY", total
    if total <= -2:
        return "SELL", total
    return "NEUTRAL", total


def _rsi_signal(
    rsi_latest: IndicatorPoint | None,
    oversold: float,
    overbought: float,
) -> SignalDetail:
    if rsi_latest is None or rsi_latest.value is None:
        return SignalDetail(
            name="rsi",
            action="NEUTRAL",
            score=0,
            confidence=0.0,
            reason="insufficient_data",
        )

    rsi_val = rsi_latest.value
    date = rsi_latest.date
    close = rsi_latest.close

    if rsi_val <= 20:
        return SignalDetail(
            name="rsi",
            action="BUY",
            score=2,
            confidence=_compute_confidence(2),
            reason="strong_oversold",
            signal_date=date,
            close=close,
            metadata={"rsi": rsi_val},
        )
    if rsi_val <= oversold:
        return SignalDetail(
            name="rsi",
            action="BUY",
            score=1,
            confidence=_compute_confidence(1),
            reason="oversold",
            signal_date=date,
            close=close,
            metadata={"rsi": rsi_val},
        )
    if rsi_val >= 80:
        return SignalDetail(
            name="rsi",
            action="SELL",
            score=-2,
            confidence=_compute_confidence(-2),
            reason="strong_overbought",
            signal_date=date,
            close=close,
            metadata={"rsi": rsi_val},
        )
    if rsi_val >= overbought:
        return SignalDetail(
            name="rsi",
            action="SELL",
            score=-1,
            confidence=_compute_confidence(-1),
            reason="overbought",
            signal_date=date,
            close=close,
            metadata={"rsi": rsi_val},
        )

    return SignalDetail(
        name="rsi",
        action="NEUTRAL",
        score=0,
        confidence=0.0,
        reason="neutral",
        signal_date=date,
        close=close,
        metadata={"rsi": rsi_val},
    )


def _macd_signal(
    macd_points: list[MacdPoint],
) -> SignalDetail:
    complete = [mp for mp in macd_points if mp.macd is not None and mp.signal is not None]
    if len(complete) < 2:
        if complete:
            return SignalDetail(
                name="macd",
                action="NEUTRAL",
                score=0,
                confidence=0.0,
                reason="insufficient_data",
                signal_date=complete[-1].date,
                close=complete[-1].close,
                metadata={"macd": complete[-1].macd, "signal": complete[-1].signal},
            )
        return SignalDetail(
            name="macd",
            action="NEUTRAL",
            score=0,
            confidence=0.0,
            reason="insufficient_data",
        )

    prev = complete[-2]
    latest = complete[-1]

    bullish = prev.macd <= prev.signal and latest.macd > latest.signal
    bearish = prev.macd >= prev.signal and latest.macd < latest.signal

    if bullish:
        return SignalDetail(
            name="macd",
            action="BUY",
            score=2,
            confidence=_compute_confidence(2),
            reason="bullish_crossover",
            signal_date=latest.date,
            close=latest.close,
            metadata={
                "macd": latest.macd,
                "signal": latest.signal,
                "histogram": latest.histogram,
            },
        )
    if bearish:
        return SignalDetail(
            name="macd",
            action="SELL",
            score=-2,
            confidence=_compute_confidence(-2),
            reason="bearish_crossover",
            signal_date=latest.date,
            close=latest.close,
            metadata={
                "macd": latest.macd,
                "signal": latest.signal,
                "histogram": latest.histogram,
            },
        )

    return SignalDetail(
        name="macd",
        action="NEUTRAL",
        score=0,
        confidence=0.0,
        reason="no_crossover",
        signal_date=latest.date,
        close=latest.close,
        metadata={
            "macd": latest.macd,
            "signal": latest.signal,
            "histogram": latest.histogram,
        },
    )


def _sma_trend_signal(
    sma_short_latest: IndicatorPoint | None,
    sma_long_latest: IndicatorPoint | None,
    close: float | None,
) -> SignalDetail:
    if sma_short_latest is None or sma_long_latest is None:
        return SignalDetail(
            name="sma_trend",
            action="NEUTRAL",
            score=0,
            confidence=0.0,
            reason="insufficient_data",
        )
    if sma_short_latest.value is None or sma_long_latest.value is None:
        return SignalDetail(
            name="sma_trend",
            action="NEUTRAL",
            score=0,
            confidence=0.0,
            reason="insufficient_data",
        )
    if close is None:
        return SignalDetail(
            name="sma_trend",
            action="NEUTRAL",
            score=0,
            confidence=0.0,
            reason="insufficient_data",
        )

    short_val = sma_short_latest.value
    long_val = sma_long_latest.value
    date = sma_short_latest.date

    if close > short_val > long_val:
        return SignalDetail(
            name="sma_trend",
            action="BUY",
            score=1,
            confidence=_compute_confidence(1),
            reason="uptrend",
            signal_date=date,
            close=close,
            metadata={"sma_short": short_val, "sma_long": long_val},
        )
    if close < short_val < long_val:
        return SignalDetail(
            name="sma_trend",
            action="SELL",
            score=-1,
            confidence=_compute_confidence(-1),
            reason="downtrend",
            signal_date=date,
            close=close,
            metadata={"sma_short": short_val, "sma_long": long_val},
        )

    return SignalDetail(
        name="sma_trend",
        action="NEUTRAL",
        score=0,
        confidence=0.0,
        reason="mixed",
        signal_date=date,
        close=close,
        metadata={"sma_short": short_val, "sma_long": long_val},
    )


def _ema_trend_signal(
    ema_short_latest: IndicatorPoint | None,
    ema_long_latest: IndicatorPoint | None,
    close: float | None,
) -> SignalDetail:
    if ema_short_latest is None or ema_long_latest is None:
        return SignalDetail(
            name="ema_trend",
            action="NEUTRAL",
            score=0,
            confidence=0.0,
            reason="insufficient_data",
        )
    if ema_short_latest.value is None or ema_long_latest.value is None:
        return SignalDetail(
            name="ema_trend",
            action="NEUTRAL",
            score=0,
            confidence=0.0,
            reason="insufficient_data",
        )
    if close is None:
        return SignalDetail(
            name="ema_trend",
            action="NEUTRAL",
            score=0,
            confidence=0.0,
            reason="insufficient_data",
        )

    short_val = ema_short_latest.value
    long_val = ema_long_latest.value
    date = ema_short_latest.date

    if close > short_val > long_val:
        return SignalDetail(
            name="ema_trend",
            action="BUY",
            score=1,
            confidence=_compute_confidence(1),
            reason="uptrend",
            signal_date=date,
            close=close,
            metadata={"ema_short": short_val, "ema_long": long_val},
        )
    if close < short_val < long_val:
        return SignalDetail(
            name="ema_trend",
            action="SELL",
            score=-1,
            confidence=_compute_confidence(-1),
            reason="downtrend",
            signal_date=date,
            close=close,
            metadata={"ema_short": short_val, "ema_long": long_val},
        )

    return SignalDetail(
        name="ema_trend",
        action="NEUTRAL",
        score=0,
        confidence=0.0,
        reason="mixed",
        signal_date=date,
        close=close,
        metadata={"ema_short": short_val, "ema_long": long_val},
    )


class SignalService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.market_data_service = MarketDataService(session)
        self.analytics_service = AnalyticsService(session)

    def get_signal_summary(
        self,
        ticker: str,
        period: str = "6mo",
        interval: str = "1d",
        refresh: bool = False,
        rsi_window: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        sma_short: int = 20,
        sma_long: int = 50,
        ema_short: int = 12,
        ema_long: int = 26,
    ) -> SignalSummaryResponse:
        history = self.market_data_service.get_history(ticker, period, interval, refresh)
        if not history.rows:
            raise MarketDataProviderError("No historical data available for calculation")

        rows = history.rows
        n_candles = len(rows)
        latest_close = rows[-1].close if rows else None
        logger.info("Generating signals for %s: %d candles, provider=%s, cached=%s, period=%s",
                    ticker, n_candles, history.provider, history.cached, period)

        sma_rows, sma_short_latest = self.analytics_service._compute_indicator_rows(
            rows, "sma", sma_short,
        )
        _, sma_long_latest = self.analytics_service._compute_indicator_rows(
            rows, "sma", sma_long,
        )

        ema_rows, ema_short_latest = self.analytics_service._compute_indicator_rows(
            rows, "ema", ema_short,
        )
        _, ema_long_latest = self.analytics_service._compute_indicator_rows(
            rows, "ema", ema_long,
        )

        rsi_rows, rsi_latest = self.analytics_service._compute_rsi_rows(rows, rsi_window)

        macd_points, _ = self.analytics_service._compute_macd_rows(
            rows, macd_fast, macd_slow, macd_signal,
        )

        signals: list[SignalDetail] = [
            _rsi_signal(rsi_latest, rsi_oversold, rsi_overbought),
            _macd_signal(macd_points),
            _sma_trend_signal(sma_short_latest, sma_long_latest, latest_close),
            _ema_trend_signal(ema_short_latest, ema_long_latest, latest_close),
        ]

        rating, total_score = _aggregate_rating(signals)
        confidence = _compute_confidence(total_score)

        logger.info("Signals generated for %s: rating=%s, score=%d/%d, confidence=%.1f%%, provider=%s, cached=%s",
                    ticker, rating, total_score, MAX_ABS_SCORE, confidence * 100, history.provider, history.cached)

        return SignalSummaryResponse(
            ticker=history.ticker,
            rating=rating,
            score=total_score,
            confidence=confidence,
            period=period,
            interval=interval,
            parameters={
                "rsi_window": rsi_window,
                "rsi_oversold": rsi_oversold,
                "rsi_overbought": rsi_overbought,
                "macd_fast": macd_fast,
                "macd_slow": macd_slow,
                "macd_signal": macd_signal,
                "sma_short": sma_short,
                "sma_long": sma_long,
                "ema_short": ema_short,
                "ema_long": ema_long,
            },
            signals=signals,
            provider=history.provider,
            cached=history.cached,
            fetched_at=history.fetched_at,
            generated_at=datetime.now(timezone.utc),
        )
