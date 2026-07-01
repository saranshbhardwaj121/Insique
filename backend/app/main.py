from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import api_router
from backend.app.core.config import get_settings
from backend.app.services.scheduler import start_alert_scheduler, stop_alert_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_alert_scheduler()
    yield
    stop_alert_scheduler()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": settings.project_name}
