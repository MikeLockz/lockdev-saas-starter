from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDMixin


class Appointment(Base, UUIDMixin, TimestampMixin):
    """
    Appointment model representing a scheduled visit between a patient and a provider.
    """

    __tablename__ = "appointments"

    # Foreign Keys
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    patient_id: Mapped[UUID] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id: Mapped[UUID] = mapped_column(
        ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Schedule details
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    # Status: SCHEDULED, CONFIRMED, COMPLETED, CANCELLED, NO_SHOW
    status: Mapped[str] = mapped_column(String, default="SCHEDULED", nullable=False)

    # Type: INITIAL, FOLLOW_UP, URGENT
    appointment_type: Mapped[str] = mapped_column(String, default="FOLLOW_UP", nullable=False)

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Cancellation details
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    organization = relationship("Organization", lazy="joined")
    patient = relationship("Patient", lazy="joined", foreign_keys=[patient_id])
    provider = relationship("Provider", lazy="joined", foreign_keys=[provider_id])
    canceller = relationship("User", foreign_keys=[cancelled_by])
