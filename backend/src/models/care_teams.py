from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
from .mixins import UUIDMixin, TimestampMixin


class CareTeamAssignment(Base, UUIDMixin, TimestampMixin):
    """
    Links Providers to Patients as part of their care team.
    Each patient can have multiple providers with different roles.
    Only one provider can be PRIMARY at a time per patient.
    """
    __tablename__ = "care_team_assignments"

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False
    )
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patients.id"), nullable=False
    )
    provider_id: Mapped[UUID] = mapped_column(
        ForeignKey("providers.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default="SPECIALIST"
    )  # PRIMARY, SPECIALIST, CONSULTANT
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    removed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    organization: Mapped["Organization"] = relationship()
    patient: Mapped["Patient"] = relationship()
    provider: Mapped["Provider"] = relationship(back_populates="care_team_assignments")

    __table_args__ = (
        # Only one active assignment per patient-provider pair
        UniqueConstraint(
            "patient_id", "provider_id",
            name="uq_care_team_patient_provider"
        ),
        # Index for filtering active assignments
        Index(
            "ix_care_team_active",
            "patient_id",
            postgresql_where=(removed_at == None)
        ),
        {"comment": "Care team assignments linking providers to patients"},
    )
