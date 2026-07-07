from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_verified_user, get_session
from backend.app.models.user import User
from backend.app.schemas.notification import NotificationRead, UnreadCountResponse, NotificationPreferences
from backend.app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    unread_only: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[NotificationRead]:
    service = NotificationService(session)
    notifications = service.list_notifications(current_user.id, limit, offset, unread_only)
    return [NotificationRead.model_validate(n) for n in notifications]


@router.get("/count", response_model=UnreadCountResponse)
def unread_count(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UnreadCountResponse:
    service = NotificationService(session)
    count = service.get_unread_count(current_user.id)
    return UnreadCountResponse(count=count)


@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> NotificationRead:
    service = NotificationService(session)
    try:
        notification = service.mark_read(current_user.id, notification_id)
        return NotificationRead.model_validate(notification)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.patch("/read-all", response_model=UnreadCountResponse)
def mark_all_notifications_read(
    current_user: User = Depends(get_verified_user),
    session: Session = Depends(get_session),
) -> UnreadCountResponse:
    service = NotificationService(session)
    service.mark_all_read(current_user.id)
    return UnreadCountResponse(count=0)


@router.get("/preferences", response_model=NotificationPreferences)
def get_notification_preferences(
    current_user: User = Depends(get_current_user),
) -> NotificationPreferences:
    return NotificationPreferences()


@router.patch("/preferences", response_model=NotificationPreferences)
def update_notification_preferences(
    current_user: User = Depends(get_current_user),
) -> NotificationPreferences:
    return NotificationPreferences()
