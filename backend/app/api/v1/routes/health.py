import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.api.deps import get_session

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthStatus(BaseModel):
    database: str
    market_data_table: str
    invalid_cache_rows: int
    status: str


@router.get("/health", response_model=HealthStatus)
def health_check(session: Session = Depends(get_session)) -> HealthStatus:
    db_ok = "unreachable"
    table_ok = "unreachable"
    invalid_count = -1

    try:
        session.execute(text("SELECT 1"))
        db_ok = "reachable"
    except Exception as exc:
        logger.error("Health check — database unreachable: %s", exc)
        return HealthStatus(
            database="unreachable",
            market_data_table="unreachable",
            invalid_cache_rows=-1,
            status="unhealthy",
        )

    try:
        session.execute(text("SELECT COUNT(*) FROM market_data"))
        table_ok = "accessible"
    except Exception as exc:
        logger.error("Health check — market_data table inaccessible: %s", exc)
        return HealthStatus(
            database=db_ok,
            market_data_table="inaccessible",
            invalid_cache_rows=-1,
            status="unhealthy",
        )

    try:
        result = session.execute(text("""
            SELECT COUNT(*) FROM market_data
            WHERE close IS NULL OR close != close
               OR open IS NULL OR open != open
               OR high IS NULL OR high != high
               OR low IS NULL OR low != low
               OR volume IS NULL OR volume != volume
        """))
        invalid_count = result.scalar() or 0
        if invalid_count > 0:
            logger.warning("Health check — %d invalid rows in market_data cache", invalid_count)
    except Exception as exc:
        logger.error("Health check — could not scan for invalid rows: %s", exc)

    status = "healthy" if invalid_count == 0 else "degraded"
    return HealthStatus(
        database=db_ok,
        market_data_table=table_ok,
        invalid_cache_rows=invalid_count,
        status=status,
    )
