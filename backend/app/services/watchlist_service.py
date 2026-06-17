from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.watchlist import Watchlist
from backend.app.models.watchlist_item import WatchlistItem
from backend.app.repositories.watchlist_repository import WatchlistRepository


class WatchlistService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = WatchlistRepository(session)

    def _normalize_name(self, name: str) -> str:
        return name.strip()

    def _normalize_ticker(self, ticker: str) -> str:
        return ticker.strip().upper()

    def create_watchlist(self, user: User, name: str) -> Watchlist:
        name = self._normalize_name(name)
        if not name:
            raise ValueError("Watchlist name cannot be empty")
        existing = self.repo.get_by_user_and_name(user.id, name)
        if existing is not None:
            raise ValueError(f"Watchlist '{name}' already exists")
        watchlist = Watchlist(user_id=user.id, name=name)
        self.repo.create(watchlist)
        try:
            self.session.commit()
            self.session.refresh(watchlist)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError(f"Watchlist '{name}' already exists") from exc
        return watchlist

    def list_watchlists(self, user: User) -> list[Watchlist]:
        return list(self.repo.list_for_user(user.id))

    def get_watchlist(self, user: User, watchlist_id: UUID) -> Watchlist:
        watchlist = self.repo.get_owned_by_id(user.id, watchlist_id)
        if watchlist is None:
            raise ValueError("Watchlist not found")
        return watchlist

    def rename_watchlist(self, user: User, watchlist_id: UUID, name: str) -> Watchlist:
        name = self._normalize_name(name)
        if not name:
            raise ValueError("Watchlist name cannot be empty")
        watchlist = self.repo.get_owned_by_id(user.id, watchlist_id)
        if watchlist is None:
            raise ValueError("Watchlist not found")
        existing = self.repo.get_by_user_and_name(user.id, name)
        if existing is not None and existing.id != watchlist_id:
            raise ValueError(f"Watchlist '{name}' already exists")
        watchlist.name = name
        try:
            self.session.commit()
            self.session.refresh(watchlist)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError(f"Watchlist '{name}' already exists") from exc
        return watchlist

    def delete_watchlist(self, user: User, watchlist_id: UUID) -> None:
        watchlist = self.repo.get_owned_by_id(user.id, watchlist_id)
        if watchlist is None:
            raise ValueError("Watchlist not found")
        self.repo.delete(watchlist)
        self.session.commit()

    def add_ticker(self, user: User, watchlist_id: UUID, ticker: str) -> WatchlistItem:
        ticker = self._normalize_ticker(ticker)
        if not ticker:
            raise ValueError("Ticker cannot be empty")
        watchlist = self.repo.get_owned_by_id(user.id, watchlist_id)
        if watchlist is None:
            raise ValueError("Watchlist not found")
        existing = self.repo.get_item_by_ticker(watchlist_id, ticker)
        if existing is not None:
            raise ValueError(f"Ticker '{ticker}' already exists in watchlist")
        item = WatchlistItem(watchlist_id=watchlist_id, ticker=ticker)
        self.repo.add_item(item)
        try:
            self.session.commit()
            self.session.refresh(item)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError(f"Ticker '{ticker}' already exists in watchlist") from exc
        return item

    def remove_ticker(self, user: User, watchlist_id: UUID, ticker: str) -> None:
        ticker = self._normalize_ticker(ticker)
        watchlist = self.repo.get_owned_by_id(user.id, watchlist_id)
        if watchlist is None:
            raise ValueError("Watchlist not found")
        item = self.repo.get_item_by_ticker(watchlist_id, ticker)
        if item is None:
            raise ValueError("Ticker not found")
        self.repo.delete_item(item)
        self.session.commit()
