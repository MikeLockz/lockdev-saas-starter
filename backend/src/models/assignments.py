from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Boolean, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
from .mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin

class PatientProxyAssignment(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "patient_proxy_assignments"

    proxy_id: Mapped[UUID] = mapped_column(ForeignKey("proxies.id"), nullable=False)
    patient_id: Mapped[UUID] = mapped_column(ForeignKey("patients.id"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False) # PARENT, POA
    
    can_view_clinical_notes: Mapped[bool] = mapped_column(Boolean, default=False)
    can_view_billing: Mapped[bool] = mapped_column(Boolean, default=True)
    can_schedule_appointments: Mapped[bool] = mapped_column(Boolean, default=True)
    
    access_granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    proxy: Mapped["Proxy"] = relationship(back_populates="patients")
    patient: Mapped["Patient"] = relationship(back_populates="proxies")

    __table_args__ = (UniqueConstraint("proxy_id", "patient_id"),)
