from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_session
from backend.app.models.user import User
from backend.app.schemas.analytics import IndicatorResponse, MacdResponse
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.market_data_service import (
    MarketDataProviderError,
    MarketDataValidationError,
)

router = APIRouter()


@router.get("/{ticker}/sma", response_model=IndicatorResponse)
def get_sma(
    ticker: str,
    window: int = Query(default=20, ge=AnalyticsService.MIN_WINDOW, le=AnalyticsService.MAX_WINDOW),
    period: str = Query(default="6mo"),
    interval: str = Query(default="1d"),
    refresh: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> IndicatorResponse:
    del current_user
    service = AnalyticsService(session)
    try:
        return service.get_sma(ticker, window, period, interval, refresh)
    except MarketDataValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MarketDataProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/{ticker}/ema", response_model=IndicatorResponse)
def get_ema(
    ticker: str,
    window: int = Query(default=20, ge=AnalyticsService.MIN_WINDOW, le=AnalyticsService.MAX_WINDOW),
    period: str = Query(default="6mo"),
    interval: str = Query(default="1d"),
    refresh: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> IndicatorResponse:
    del current_user
    service = AnalyticsService(session)
    try:
        return service.get_ema(ticker, window, period, interval, refresh)
    except MarketDataValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MarketDataProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/{ticker}/rsi", response_model=IndicatorResponse)
def get_rsi(
    ticker: str,
    window: int = Query(default=14, ge=AnalyticsService.MIN_WINDOW, le=AnalyticsService.MAX_WINDOW),
    period: str = Query(default="6mo"),
    interval: str = Query(default="1d"),
    refresh: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> IndicatorResponse:
    del current_user
    service = AnalyticsService(session)
    try:
        return service.get_rsi(ticker, window, period, interval, refresh)
    except MarketDataValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MarketDataProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/{ticker}/macd", response_model=MacdResponse)
def get_macd(
    ticker: str,
    fast: int = Query(default=12, ge=2, le=250),
    slow: int = Query(default=26, ge=2, le=250),
    signal: int = Query(default=9, ge=2, le=250),
    period: str = Query(default="6mo"),
    interval: str = Query(default="1d"),
    refresh: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MacdResponse:
    del current_user
    service = AnalyticsService(session)
    try:
        return service.get_macd(ticker, fast, slow, signal, period, interval, refresh)
    except MarketDataValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MarketDataProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
