from fastapi import APIRouter, Depends

from backend.app.api.deps import get_current_user

router = APIRouter()


@router.get("/status")
def trades_status(current_user=Depends(get_current_user)) -> dict[str, str]:
    return {"status": "trades module ready"}
