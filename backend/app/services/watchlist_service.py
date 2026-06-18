from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.watchlist import Watchlist
from backend.app.models.watchlist_item import WatchlistItem
from backend.app.repositories.watchlist_repository import WatchlistRepository
from backend.app.schemas.watchlist import (
    WatchlistQuoteItemRead,
    WatchlistQuotesResponse,
    WatchlistSignalItemRead,
    WatchlistSignalsResponse,
)
from backend.app.services.signal_service import SignalService
from backend.app.services.market_data_service import (
    MarketDataProviderError,
    MarketDataService,
    MarketDataValidationError,
)


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

    def get_watchlist_quotes(self, user: User, watchlist_id: UUID) -> WatchlistQuotesResponse:
        watchlist = self.get_watchlist(user, watchlist_id)
        fetched_at = datetime.now(timezone.utc)
        market_data_service = MarketDataService(self.session)

        seen: set[str] = set()
        unique_ordered_tickers: list[str] = []
        for item in watchlist.items:
            if item.ticker not in seen:
                seen.add(item.ticker)
                unique_ordered_tickers.append(item.ticker)

        quotes: list[WatchlistQuoteItemRead] = []
        for ticker in unique_ordered_tickers:
            try:
                quote = market_data_service.get_quote(ticker)
                quotes.append(
                    WatchlistQuoteItemRead(
                        ticker=quote.ticker,
                        name=quote.name,
                        currency=quote.currency,
                        price=quote.price,
                        previous_close=quote.previous_close,
                        open=quote.open,
                        day_high=quote.day_high,
                        day_low=quote.day_low,
                        volume=quote.volume,
                        market_cap=quote.market_cap,
                        exchange=quote.exchange,
                        provider=quote.provider,
                        fetched_at=quote.fetched_at,
                    )
                )
            except (MarketDataValidationError, MarketDataProviderError) as exc:
                quotes.append(
                    WatchlistQuoteItemRead(
                        ticker=ticker,
                        error=str(exc),
                    )
                )

        return WatchlistQuotesResponse(
            watchlist_id=watchlist.id,
            watchlist_name=watchlist.name,
            quotes=quotes,
            fetched_at=fetched_at,
        )

    def get_watchlist_signals(
        self,
        user: User,
        watchlist_id: UUID,
        period: str = "6mo",
        interval: str = "1d",
        refresh: bool = False,
        rsi_window: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        sma_short: int = 20,
        sma_long: int = 50,
        ema_short: int = 12,
        ema_long: int = 26,
    ) -> WatchlistSignalsResponse:
        watchlist = self.get_watchlist(user, watchlist_id)
        generated_at = datetime.now(timezone.utc)
        signal_service = SignalService(self.session)

        signals: list[WatchlistSignalItemRead] = []
        for item in watchlist.items:
            try:
                summary = signal_service.get_signal_summary(
                    ticker=item.ticker,
                    period=period,
                    interval=interval,
                    refresh=refresh,
                    rsi_window=rsi_window,
                    rsi_oversold=rsi_oversold,
                    rsi_overbought=rsi_overbought,
                    macd_fast=macd_fast,
                    macd_slow=macd_slow,
                    macd_signal=macd_signal,
                    sma_short=sma_short,
                    sma_long=sma_long,
                    ema_short=ema_short,
                    ema_long=ema_long,
                )
                signals.append(
                    WatchlistSignalItemRead(ticker=item.ticker, summary=summary)
                )
            except (MarketDataValidationError, MarketDataProviderError) as exc:
                signals.append(
                    WatchlistSignalItemRead(ticker=item.ticker, error=str(exc))
                )

        return WatchlistSignalsResponse(
            watchlist_id=watchlist.id,
            watchlist_name=watchlist.name,
            period=period,
            interval=interval,
            parameters={
                "rsi_window": rsi_window,
                "rsi_oversold": rsi_oversold,
                "rsi_overbought": rsi_overbought,
                "macd_fast": macd_fast,
                "macd_slow": macd_slow,
                "macd_signal": macd_signal,
                "sma_short": sma_short,
                "sma_long": sma_long,
                "ema_short": ema_short,
                "ema_long": ema_long,
            },
            signals=signals,
            generated_at=generated_at,
        )

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
