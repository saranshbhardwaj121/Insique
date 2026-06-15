from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def watchlists_status() -> dict[str, str]:
    return {"status": "watchlists module ready"}
