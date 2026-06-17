from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
