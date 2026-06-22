from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HoldingCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20, description="Stock ticker symbol")
    quantity: float = Field(..., gt=0, description="Number of shares/units")
    average_cost_basis: float = Field(..., gt=0, description="Average price paid per unit")


class HoldingUpdate(BaseModel):
    quantity: float | None = Field(default=None, gt=0)
    average_cost_basis: float | None = Field(default=None, gt=0)


class HoldingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticker: str
    quantity: float
    average_cost_basis: float
    created_at: datetime
    updated_at: datetime


class HoldingWithMetricsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticker: str
    quantity: float
    average_cost_basis: float
    current_price: float | None = None
    market_value: float | None = None
    profit_loss: float | None = None
    profit_loss_percent: float | None = None
    allocation_percent: float | None = None
    created_at: datetime
    updated_at: datetime


class PortfolioSummaryRead(BaseModel):
    total_market_value: float
    total_cost_basis: float
    total_profit_loss: float
    total_profit_loss_percent: float
    total_holdings: int
    profitable_holdings: int
    losing_holdings: int
    holdings: list[HoldingWithMetricsRead]
