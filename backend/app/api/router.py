from fastapi import APIRouter

from backend.app.api.v1.routes import auth, health, market_data, trades, watchlists

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(watchlists.router, prefix="/watchlists", tags=["watchlists"])
api_router.include_router(market_data.router, prefix="/market-data", tags=["market-data"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
