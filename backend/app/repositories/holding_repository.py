from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.holding import Holding


class HoldingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, holding: Holding) -> Holding:
        self.session.add(holding)
        return holding

    def list_for_user(self, user_id: UUID) -> Sequence[Holding]:
        statement = (
            select(Holding)
            .where(Holding.user_id == user_id)
            .order_by(Holding.ticker.asc())
        )
        return self.session.scalars(statement).all()

    def get_owned_by_id(self, user_id: UUID, holding_id: UUID) -> Holding | None:
        statement = select(Holding).where(
            Holding.id == holding_id, Holding.user_id == user_id
        )
        return self.session.scalar(statement)

    def get_by_user_and_ticker(self, user_id: UUID, ticker: str) -> Holding | None:
        statement = select(Holding).where(
            Holding.user_id == user_id, Holding.ticker == ticker
        )
        return self.session.scalar(statement)

    def delete(self, holding: Holding) -> None:
        self.session.delete(holding)
