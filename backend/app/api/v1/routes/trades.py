from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def trades_status() -> dict[str, str]:
    return {"status": "trades module ready"}
