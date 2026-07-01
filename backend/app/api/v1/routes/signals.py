from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_session
from backend.app.schemas.signals import SignalSummaryResponse
from backend.app.services.market_data_service import (
    MarketDataProviderError,
    MarketDataValidationError,
)
from backend.app.services.signal_service import SignalService

router = APIRouter()


@router.get("/{ticker}", response_model=SignalSummaryResponse)
def get_signal_summary(
    ticker: str,
    period: str = Query(default="6mo"),
    interval: str = Query(default="1d"),
    refresh: bool = Query(default=False),
    rsi_window: int = Query(default=14, ge=2, le=250),
    rsi_oversold: float = Query(default=30, ge=0, le=100),
    rsi_overbought: float = Query(default=70, ge=0, le=100),
    macd_fast: int = Query(default=12, ge=2, le=250),
    macd_slow: int = Query(default=26, ge=2, le=250),
    macd_signal: int = Query(default=9, ge=2, le=250),
    sma_short: int = Query(default=20, ge=2, le=250),
    sma_long: int = Query(default=50, ge=2, le=250),
    ema_short: int = Query(default=12, ge=2, le=250),
    ema_long: int = Query(default=26, ge=2, le=250),
    session: Session = Depends(get_session),
) -> SignalSummaryResponse:

    if rsi_oversold >= rsi_overbought:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="rsi_oversold must be less than rsi_overbought",
        )
    if macd_slow <= macd_fast:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="macd_slow must be greater than macd_fast",
        )
    if sma_long <= sma_short:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sma_long must be greater than sma_short",
        )
    if ema_long <= ema_short:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ema_long must be greater than ema_short",
        )

    service = SignalService(session)
    try:
        return service.get_signal_summary(
            ticker=ticker,
            period=period,
            interval=interval,
            refresh=refresh,
            rsi_window=rsi_window,
            rsi_oversold=rsi_oversold,
            rsi_overbought=rsi_overbought,
            macd_fast=macd_fast,
            macd_slow=macd_slow,
            macd_signal=macd_signal,
            sma_short=sma_short,
            sma_long=sma_long,
            ema_short=ema_short,
            ema_long=ema_long,
        )
    except MarketDataValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MarketDataProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
