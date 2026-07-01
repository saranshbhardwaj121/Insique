import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Numeric, String, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin


class Alert(TimestampMixin, Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(20), nullable=False)
    operator: Mapped[str] = mapped_column(String(5), nullable=False)
    threshold: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    user = relationship("User", back_populates="alerts")
    triggered_alerts = relationship(
        "TriggeredAlert",
        back_populates="alert",
        cascade="all, delete-orphan",
        order_by="TriggeredAlert.triggered_at.desc()",
    )
    notifications = relationship("Notification", back_populates="alert", cascade="all, delete-orphan")


class TriggeredAlert(Base):
    __tablename__ = "triggered_alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alerts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(20), nullable=False)
    operator: Mapped[str] = mapped_column(String(5), nullable=False)
    threshold: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    triggered_value: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    snapshot: Mapped[dict | None] = mapped_column("snapshot", JSONB, nullable=True)

    alert = relationship("Alert", back_populates="triggered_alerts")
