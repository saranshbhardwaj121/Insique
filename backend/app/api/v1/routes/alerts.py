from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_verified_user, get_session
from backend.app.models.user import User
from backend.app.schemas.alert import AlertCreate, AlertRead, AlertUpdate, TriggeredAlertRead
from backend.app.services.alert_service import AlertService

router = APIRouter()


@router.get("", response_model=list[AlertRead])
def list_alerts(
    status: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[AlertRead]:
    service = AlertService(session)
    alerts_with_counts = service.list_alerts_with_counts(current_user, status)
    return [
        AlertRead(
            **alert.__dict__,
            trigger_count=count,
        )
        for alert, count in alerts_with_counts
    ]


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
def create_alert(
    payload: AlertCreate,
    current_user: User = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> AlertRead:
    service = AlertService(session)
    try:
        alert = service.create_alert(current_user, payload)
        return AlertRead(
            **alert.__dict__,
            trigger_count=0,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> AlertRead:
    service = AlertService(session)
    try:
        alert = service.get_alert(current_user, alert_id)
        return AlertRead(
            **alert.__dict__,
            trigger_count=service.get_trigger_count(alert.id),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.patch("/{alert_id}", response_model=AlertRead)
def update_alert(
    alert_id: UUID,
    payload: AlertUpdate,
    current_user: User = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> AlertRead:
    service = AlertService(session)
    try:
        alert = service.update_alert(current_user, alert_id, payload)
        return AlertRead(
            **alert.__dict__,
            trigger_count=service.get_trigger_count(alert.id),
        )
    except ValueError as exc:
        detail = str(exc)
        if "not found" in detail.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=detail
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from exc


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: UUID,
    current_user: User = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> None:
    service = AlertService(session)
    try:
        service.delete_alert(current_user, alert_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.get("/{alert_id}/triggers", response_model=list[TriggeredAlertRead])
def get_alert_triggers(
    alert_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[TriggeredAlertRead]:
    service = AlertService(session)
    try:
        triggers, _ = service.get_trigger_history(
            current_user, alert_id, limit, offset
        )
        return [TriggeredAlertRead.model_validate(t) for t in triggers]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
