import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, pk_ulid


class Appointment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "appointments"

    id: Mapped[pk_ulid]
    organization_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id"), index=True
    )
    patient_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("patients.id"), index=True
    )
    provider_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("providers.id"), index=True
    )

    scheduled_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), index=True
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[str] = mapped_column(
        String(20), default="SCHEDULED"
    )  # SCHEDULED, CONFIRMED, COMPLETED, CANCELLED, NO_SHOW
    appointment_type: Mapped[str] = mapped_column(
        String(20), default="INITIAL"
    )  # INITIAL, FOLLOW_UP, URGENT

    reason: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    cancelled_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    cancelled_by: Mapped[str | None] = mapped_column(String(26), ForeignKey("users.id"))
    cancellation_reason: Mapped[str | None] = mapped_column(String(255))

    organization: Mapped["Organization"] = relationship()
    patient: Mapped["Patient"] = relationship()
    provider: Mapped["Provider"] = relationship()
