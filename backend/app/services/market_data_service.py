from collections.abc import Iterable
from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from backend.app.models.market_data import MarketData


class MarketDataService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_history(self, ticker: str, frame: pd.DataFrame) -> int:
        rows: list[MarketData] = []
        for index, row in frame.iterrows():
            row_date = index.date() if hasattr(index, "date") else index
            rows.append(
                MarketData(
                    ticker=ticker.upper(),
                    date=row_date if isinstance(row_date, date) else row_date.to_pydatetime().date(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                )
            )

        if rows:
            self.session.add_all(rows)
            self.session.commit()

        return len(rows)

    def list_cached_ticker(self, ticker: str) -> Iterable[MarketData]:
        return self.session.query(MarketData).filter(MarketData.ticker == ticker.upper()).order_by(MarketData.date.asc()).all()
