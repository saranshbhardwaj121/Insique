from datetime import date, datetime
from typing import Optional, Union

from pydantic import BaseModel


class SignalDetail(BaseModel):
    name: str
    action: str
    score: int
    confidence: float
    reason: str
    signal_date: Optional[date] = None
    close: Optional[float] = None
    metadata: dict[str, Union[float, int, str, None]] = {}


class SignalSummaryResponse(BaseModel):
    ticker: str
    rating: str
    score: int
    confidence: float
    period: str
    interval: str
    parameters: dict[str, Union[int, float]]
    signals: list[SignalDetail]
    provider: str
    cached: bool
    fetched_at: datetime
    generated_at: datetime
