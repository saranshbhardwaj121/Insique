from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.app.schemas.search import SearchResponse
from backend.app.services.search_service import SearchProviderError, SearchService

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
def search_tickers(
    q: str = Query(min_length=0, max_length=100),
    limit: int = Query(default=10, ge=1, le=50),
) -> SearchResponse | JSONResponse:
    if not q.strip():
        return SearchResponse(query=q, results=[])
    service = SearchService()
    try:
        return service.search(query=q, limit=limit)
    except SearchProviderError:
        return JSONResponse(
            status_code=502,
            content={"detail": "Search provider temporarily unavailable"},
        )
