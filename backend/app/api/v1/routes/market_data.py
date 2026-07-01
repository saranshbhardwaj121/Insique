from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_session
from backend.app.schemas.market_data import HistoricalDataResponse, QuoteRead
from backend.app.services.market_data_service import (
    MarketDataProviderError,
    MarketDataService,
    MarketDataValidationError,
)

router = APIRouter()


@router.get("/quote/{ticker}", response_model=QuoteRead)
def get_quote(
    ticker: str,
    session: Session = Depends(get_session),
) -> QuoteRead:
    service = MarketDataService(session)
    try:
        return service.get_quote(ticker)
    except MarketDataValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MarketDataProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/history/{ticker}", response_model=HistoricalDataResponse)
def get_history(
    ticker: str,
    period: str = Query(default="1mo"),
    interval: str = Query(default="1d"),
    refresh: bool = Query(default=False),
    session: Session = Depends(get_session),
) -> HistoricalDataResponse:
    service = MarketDataService(session)
    try:
        return service.get_history(
            ticker=ticker,
            period=period,
            interval=interval,
            refresh=refresh,
        )
    except MarketDataValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MarketDataProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
