from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_session
from backend.app.models.user import User
from backend.app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistItemCreate,
    WatchlistRead,
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
    current_user: User = Depends(get_current_user),
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


@router.patch("/{watchlist_id}", response_model=WatchlistRead)
def rename_watchlist(
    watchlist_id: UUID,
    payload: WatchlistUpdate,
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    service = WatchlistService(session)
    try:
        service.remove_ticker(current_user, watchlist_id, ticker)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
