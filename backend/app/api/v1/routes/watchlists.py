from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_verified_user, get_session
from backend.app.models.user import User
from backend.app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistItemCreate,
    WatchlistQuotesResponse,
    WatchlistRead,
    WatchlistSignalsResponse,
    WatchlistUpdate,
)
from backend.app.services.watchlist_service import WatchlistService

router = APIRouter()


@router.get("", response_model=list[WatchlistRead])
def list_watchlists(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[WatchlistRead]:
    service = WatchlistService(session)
    watchlists = service.list_watchlists(current_user)
    return [WatchlistRead.model_validate(w) for w in watchlists]


@router.post("", response_model=WatchlistRead, status_code=status.HTTP_201_CREATED)
def create_watchlist(
    payload: WatchlistCreate,
    current_user: User = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> WatchlistRead:
    service = WatchlistService(session)
    try:
        watchlist = service.create_watchlist(current_user, payload.name)
        return WatchlistRead.model_validate(watchlist)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.get("/{watchlist_id}", response_model=WatchlistRead)
def get_watchlist(
    watchlist_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> WatchlistRead:
    service = WatchlistService(session)
    try:
        watchlist = service.get_watchlist(current_user, watchlist_id)
        return WatchlistRead.model_validate(watchlist)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.get(
    "/{watchlist_id}/quotes",
    response_model=WatchlistQuotesResponse,
)
def get_watchlist_quotes(
    watchlist_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> WatchlistQuotesResponse:
    service = WatchlistService(session)
    try:
        return service.get_watchlist_quotes(current_user, watchlist_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.get(
    "/{watchlist_id}/signals",
    response_model=WatchlistSignalsResponse,
)
def get_watchlist_signals(
    watchlist_id: UUID,
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
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> WatchlistSignalsResponse:
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

    service = WatchlistService(session)
    try:
        return service.get_watchlist_signals(
            current_user,
            watchlist_id,
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
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.patch("/{watchlist_id}", response_model=WatchlistRead)
def rename_watchlist(
    watchlist_id: UUID,
    payload: WatchlistUpdate,
    current_user: User = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> WatchlistRead:
    service = WatchlistService(session)
    try:
        watchlist = service.rename_watchlist(current_user, watchlist_id, payload.name)
        return WatchlistRead.model_validate(watchlist)
    except ValueError as exc:
        detail = str(exc)
        if "not found" in detail.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=detail
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from exc


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watchlist(
    watchlist_id: UUID,
    current_user: User = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> None:
    service = WatchlistService(session)
    try:
        service.delete_watchlist(current_user, watchlist_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.post(
    "/{watchlist_id}/items",
    response_model=WatchlistRead,
    status_code=status.HTTP_201_CREATED,
)
def add_ticker(
    watchlist_id: UUID,
    payload: WatchlistItemCreate,
    current_user: User = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> WatchlistRead:
    service = WatchlistService(session)
    try:
        service.add_ticker(current_user, watchlist_id, payload.ticker)
        watchlist = service.get_watchlist(current_user, watchlist_id)
        return WatchlistRead.model_validate(watchlist)
    except ValueError as exc:
        detail = str(exc)
        if "not found" in detail.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=detail
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from exc


@router.delete(
    "/{watchlist_id}/items/{ticker}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_ticker(
    watchlist_id: UUID,
    ticker: str,
    current_user: User = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> None:
    service = WatchlistService(session)
    try:
        service.remove_ticker(current_user, watchlist_id, ticker)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
