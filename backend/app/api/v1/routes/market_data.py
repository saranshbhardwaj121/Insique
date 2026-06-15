from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def market_data_status() -> dict[str, str]:
    return {"status": "market data module ready"}
