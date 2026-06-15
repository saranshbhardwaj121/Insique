from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.db.session import get_db
from backend.app.schemas.health import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    settings = get_settings()
    db.execute(text("SELECT 1"))
    return HealthResponse(status="ok", environment=settings.environment, database="connected")
