from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Boolean, DateTime, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
from .mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin


class PatientProxyAssignment(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Links a Proxy (user) to a Patient with granular permissions.
    Supports time-limited access via expires_at and revocation tracking.
    """
    __tablename__ = "patient_proxy_assignments"

    proxy_id: Mapped[UUID] = mapped_column(ForeignKey("proxies.id"), nullable=False)
    patient_id: Mapped[UUID] = mapped_column(ForeignKey("patients.id"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)  # PARENT, SPOUSE, GUARDIAN, CAREGIVER, POA, OTHER

    # Granular Permissions
    can_view_profile: Mapped[bool] = mapped_column(Boolean, default=True)
    can_view_appointments: Mapped[bool] = mapped_column(Boolean, default=True)
    can_schedule_appointments: Mapped[bool] = mapped_column(Boolean, default=False)
    can_view_clinical_notes: Mapped[bool] = mapped_column(Boolean, default=False)
    can_view_billing: Mapped[bool] = mapped_column(Boolean, default=False)
    can_message_providers: Mapped[bool] = mapped_column(Boolean, default=False)

    # Time tracking
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    proxy: Mapped["Proxy"] = relationship(back_populates="patients")
    patient: Mapped["Patient"] = relationship(back_populates="proxies")

    __table_args__ = (
        UniqueConstraint("proxy_id", "patient_id"),
        Index("idx_proxy_assignments_proxy", "proxy_id"),
        Index("idx_proxy_assignments_patient", "patient_id"),
    )
