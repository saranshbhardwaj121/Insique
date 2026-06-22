from fastapi import APIRouter

from backend.app.api.v1.routes import alerts, analytics, auth, health, market_data, notifications, portfolio, search, signals, trades, watchlists

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(watchlists.router, prefix="/watchlists", tags=["watchlists"])
api_router.include_router(market_data.router, prefix="/market-data", tags=["market-data"])
api_router.include_router(search.router, prefix="/market-data", tags=["market-data"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(signals.router, prefix="/signals", tags=["signals"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
