from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.watchlist import Watchlist
from backend.app.models.watchlist_item import WatchlistItem


class WatchlistRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, watchlist: Watchlist) -> Watchlist:
        self.session.add(watchlist)
        return watchlist

    def get_by_id(self, watchlist_id: UUID) -> Watchlist | None:
        return self.session.get(Watchlist, watchlist_id)

    def get_owned_by_id(self, user_id: UUID, watchlist_id: UUID) -> Watchlist | None:
        statement = (
            select(Watchlist)
            .options(joinedload(Watchlist.items))
            .where(Watchlist.id == watchlist_id, Watchlist.user_id == user_id)
        )
        return self.session.scalar(statement)

    def list_for_user(self, user_id: UUID) -> Sequence[Watchlist]:
        statement = (
            select(Watchlist)
            .options(joinedload(Watchlist.items))
            .where(Watchlist.user_id == user_id)
            .order_by(Watchlist.created_at.asc())
        )
        return self.session.scalars(statement).unique().all()

    def get_by_user_and_name(self, user_id: UUID, name: str) -> Watchlist | None:
        statement = select(Watchlist).where(
            Watchlist.user_id == user_id, Watchlist.name == name
        )
        return self.session.scalar(statement)

    def delete(self, watchlist: Watchlist) -> None:
        self.session.delete(watchlist)

    def add_item(self, item: WatchlistItem) -> WatchlistItem:
        self.session.add(item)
        return item

    def get_item_by_ticker(
        self, watchlist_id: UUID, ticker: str
    ) -> WatchlistItem | None:
        statement = select(WatchlistItem).where(
            WatchlistItem.watchlist_id == watchlist_id,
            WatchlistItem.ticker == ticker,
        )
        return self.session.scalar(statement)

    def delete_item(self, item: WatchlistItem) -> None:
        self.session.delete(item)
