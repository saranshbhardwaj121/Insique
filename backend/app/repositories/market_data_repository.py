from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.market_data import MarketData


class MarketDataRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_by_ticker(self, ticker: str) -> list[MarketData]:
        statement = (
            select(MarketData)
            .where(MarketData.ticker == ticker)
            .order_by(MarketData.date.asc())
        )
        return list(self.session.scalars(statement).all())

    def get_by_ticker_and_date(self, ticker: str, row_date: date) -> MarketData | None:
        statement = select(MarketData).where(
            MarketData.ticker == ticker,
            MarketData.date == row_date,
        )
        return self.session.scalar(statement)

    def get_latest_updated_at(self, ticker: str) -> datetime | None:
        statement = select(func.max(MarketData.updated_at)).where(MarketData.ticker == ticker)
        return self.session.scalar(statement)

    def delete_by_ticker(self, ticker: str) -> int:
        statement = select(MarketData).where(MarketData.ticker == ticker)
        rows = list(self.session.scalars(statement).all())
        for row in rows:
            self.session.delete(row)
        return len(rows)

    def upsert_rows(self, rows: list[MarketData]) -> int:
        count = 0
        for row in rows:
            existing = self.get_by_ticker_and_date(row.ticker, row.date)
            if existing is None:
                self.session.add(row)
            else:
                existing.open = row.open
                existing.high = row.high
                existing.low = row.low
                existing.close = row.close
                existing.volume = row.volume
            count += 1
        return count
