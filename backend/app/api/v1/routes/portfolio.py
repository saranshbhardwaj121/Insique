from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_session
from backend.app.models.user import User
from backend.app.schemas.portfolio import (
    HoldingCreate,
    HoldingRead,
    HoldingUpdate,
    PortfolioSummaryRead,
)
from backend.app.services.portfolio_service import PortfolioService

router = APIRouter()


@router.get("/holdings", response_model=list[HoldingRead])
def list_holdings(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[HoldingRead]:
    service = PortfolioService(session)
    holdings = service.list_holdings(current_user)
    return [HoldingRead.model_validate(h) for h in holdings]


@router.post("/holdings", response_model=HoldingRead, status_code=status.HTTP_201_CREATED)
def add_holding(
    payload: HoldingCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> HoldingRead:
    service = PortfolioService(session)
    try:
        holding = service.add_holding(
            current_user,
            payload.ticker,
            payload.quantity,
            payload.average_cost_basis,
        )
        return HoldingRead.model_validate(holding)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.patch("/holdings/{holding_id}", response_model=HoldingRead)
def update_holding(
    holding_id: UUID,
    payload: HoldingUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> HoldingRead:
    service = PortfolioService(session)
    try:
        holding = service.update_holding(
            current_user,
            holding_id,
            payload.quantity,
            payload.average_cost_basis,
        )
        return HoldingRead.model_validate(holding)
    except ValueError as exc:
        detail = str(exc)
        if "not found" in detail.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=detail
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from exc


@router.delete("/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(
    holding_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    service = PortfolioService(session)
    try:
        service.delete_holding(current_user, holding_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.get("/summary", response_model=PortfolioSummaryRead)
def portfolio_summary(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> PortfolioSummaryRead:
    service = PortfolioService(session)
    return service.get_summary(current_user)
