from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDMixin


class Call(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "calls"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    patient_id: Mapped[UUID | None] = mapped_column(ForeignKey("patients.id"), nullable=True, index=True)
    agent_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    direction: Mapped[str] = mapped_column(String, nullable=False)  # INBOUND, OUTBOUND
    status: Mapped[str] = mapped_column(String, nullable=False, index=True)  # QUEUED, IN_PROGRESS, COMPLETED, MISSED
    phone_number: Mapped[str] = mapped_column(String, nullable=False)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # RESOLVED, CALLBACK_SCHEDULED, TRANSFERRED, VOICEMAIL

    # Relationships
    organization = relationship("Organization")
    patient = relationship("Patient")
    agent = relationship("User", foreign_keys=[agent_id])


class Task(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tasks"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    patient_id: Mapped[UUID | None] = mapped_column(ForeignKey("patients.id"), nullable=True, index=True)
    assignee_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String, nullable=False, index=True)  # TODO, IN_PROGRESS, DONE, CANCELLED
    priority: Mapped[str] = mapped_column(String, nullable=False)  # LOW, MEDIUM, HIGH, URGENT

    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization")
    patient = relationship("Patient")
    assignee = relationship("User", foreign_keys=[assignee_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
