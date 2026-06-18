from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.signals import SignalSummaryResponse


class WatchlistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class WatchlistUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class WatchlistItemCreate(BaseModel):
    ticker: str = Field(min_length=1, max_length=20)


class WatchlistItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticker: str
    created_at: datetime


class WatchlistRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    items: list[WatchlistItemRead]


class WatchlistQuoteItemRead(BaseModel):
    ticker: str
    name: str | None = None
    currency: str | None = None
    price: float | None = None
    previous_close: float | None = None
    open: float | None = None
    day_high: float | None = None
    day_low: float | None = None
    volume: int | None = None
    market_cap: int | None = None
    exchange: str | None = None
    provider: str | None = None
    fetched_at: datetime | None = None
    error: str | None = None


class WatchlistQuotesResponse(BaseModel):
    watchlist_id: UUID
    watchlist_name: str
    quotes: list[WatchlistQuoteItemRead]
    fetched_at: datetime


class WatchlistSignalItemRead(BaseModel):
    ticker: str
    summary: Optional[SignalSummaryResponse] = None
    error: Optional[str] = None


class WatchlistSignalsResponse(BaseModel):
    watchlist_id: UUID
    watchlist_name: str
    period: str
    interval: str
    parameters: dict[str, Union[float, int]]
    signals: list[WatchlistSignalItemRead]
    generated_at: datetime
