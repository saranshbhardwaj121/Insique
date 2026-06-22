from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.holding import Holding
from backend.app.models.user import User
from backend.app.repositories.holding_repository import HoldingRepository
from backend.app.schemas.portfolio import (
    HoldingRead,
    HoldingWithMetricsRead,
    PortfolioSummaryRead,
)
from backend.app.services.market_data_service import (
    MarketDataProviderError,
    MarketDataService,
    MarketDataValidationError,
)


class PortfolioService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = HoldingRepository(session)

    def _normalize_ticker(self, ticker: str) -> str:
        return ticker.strip().upper()

    def list_holdings(self, user: User) -> list[Holding]:
        return list(self.repo.list_for_user(user.id))

    def add_holding(self, user: User, ticker: str, quantity: float, average_cost_basis: float) -> Holding:
        ticker = self._normalize_ticker(ticker)
        if not ticker:
            raise ValueError("Ticker cannot be empty")
        existing = self.repo.get_by_user_and_ticker(user.id, ticker)
        if existing is not None:
            raise ValueError(f"Holding for ticker '{ticker}' already exists")
        holding = Holding(
            user_id=user.id,
            ticker=ticker,
            quantity=quantity,
            average_cost_basis=average_cost_basis,
        )
        self.repo.add(holding)
        try:
            self.session.commit()
            self.session.refresh(holding)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError(f"Holding for ticker '{ticker}' already exists") from exc
        return holding

    def update_holding(
        self, user: User, holding_id: UUID, quantity: float | None, average_cost_basis: float | None
    ) -> Holding:
        holding = self.repo.get_owned_by_id(user.id, holding_id)
        if holding is None:
            raise ValueError("Holding not found")
        if quantity is not None:
            holding.quantity = quantity
        if average_cost_basis is not None:
            holding.average_cost_basis = average_cost_basis
        try:
            self.session.commit()
            self.session.refresh(holding)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError("Failed to update holding") from exc
        return holding

    def delete_holding(self, user: User, holding_id: UUID) -> None:
        holding = self.repo.get_owned_by_id(user.id, holding_id)
        if holding is None:
            raise ValueError("Holding not found")
        self.repo.delete(holding)
        self.session.commit()

    def get_summary(self, user: User) -> PortfolioSummaryRead:
        holdings = list(self.repo.list_for_user(user.id))
        if not holdings:
            return PortfolioSummaryRead(
                total_market_value=0.0,
                total_cost_basis=0.0,
                total_profit_loss=0.0,
                total_profit_loss_percent=0.0,
                total_holdings=0,
                profitable_holdings=0,
                losing_holdings=0,
                holdings=[],
            )

        tickers = [h.ticker for h in holdings]
        price_map: dict[str, float | None] = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_map = {
                executor.submit(self._fetch_price, ticker): ticker
                for ticker in tickers
            }
            for future in as_completed(future_map):
                ticker = future_map[future]
                try:
                    price_map[ticker] = future.result()
                except Exception:
                    price_map[ticker] = None

        enriched: list[HoldingWithMetricsRead] = []
        total_market_value = 0.0
        total_cost_basis = 0.0

        for h in holdings:
            current_price = price_map.get(h.ticker)
            cost_basis = float(h.quantity) * float(h.average_cost_basis)
            market_value = float(h.quantity) * current_price if current_price is not None else None
            profit_loss = market_value - cost_basis if market_value is not None else None
            profit_loss_percent = (
                ((current_price - float(h.average_cost_basis)) / float(h.average_cost_basis)) * 100
                if current_price is not None
                else None
            )

            total_cost_basis += cost_basis
            if market_value is not None:
                total_market_value += market_value

            enriched.append(
                HoldingWithMetricsRead(
                    id=h.id,
                    ticker=h.ticker,
                    quantity=float(h.quantity),
                    average_cost_basis=float(h.average_cost_basis),
                    current_price=current_price,
                    market_value=market_value,
                    profit_loss=profit_loss,
                    profit_loss_percent=profit_loss_percent,
                    allocation_percent=None,
                    created_at=h.created_at,
                    updated_at=h.updated_at,
                )
            )

        for item in enriched:
            if item.market_value is not None and total_market_value > 0:
                item.allocation_percent = (item.market_value / total_market_value) * 100

        profitable = sum(1 for h in enriched if h.profit_loss is not None and h.profit_loss > 0)
        losing = sum(1 for h in enriched if h.profit_loss is not None and h.profit_loss < 0)
        total_profit_loss = total_market_value - total_cost_basis
        total_profit_loss_percent = (
            ((total_market_value / total_cost_basis) - 1) * 100
            if total_cost_basis > 0
            else 0.0
        )

        return PortfolioSummaryRead(
            total_market_value=round(total_market_value, 2),
            total_cost_basis=round(total_cost_basis, 2),
            total_profit_loss=round(total_profit_loss, 2),
            total_profit_loss_percent=round(total_profit_loss_percent, 2),
            total_holdings=len(holdings),
            profitable_holdings=profitable,
            losing_holdings=losing,
            holdings=enriched,
        )

    def _fetch_price(self, ticker: str) -> float | None:
        market_data_service = MarketDataService(self.session)
        try:
            quote = market_data_service.get_quote(ticker)
            return float(quote.price) if quote.price is not None else None
        except (MarketDataValidationError, MarketDataProviderError):
            return None
