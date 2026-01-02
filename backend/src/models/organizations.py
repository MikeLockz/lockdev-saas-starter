from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from .base import Base
from .mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin

class Organization(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_id: Mapped[Optional[str]] = mapped_column(String(50))
    settings_json: Mapped[dict] = mapped_column(JSONB, default={})
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(100))
    subscription_status: Mapped[str] = mapped_column(String(50), default="INCOMPLETE")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    patient_count: Mapped[int] = mapped_column(Integer, default=0)

    members: Mapped[List["OrganizationMember"]] = relationship(back_populates="organization")
    patients: Mapped[List["OrganizationPatient"]] = relationship(back_populates="organization")

class OrganizationMember(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "organization_memberships"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False) # PROVIDER, STAFF, ADMIN

    organization: Mapped["Organization"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")

    __table_args__ = (UniqueConstraint("organization_id", "user_id"),)

class OrganizationPatient(Base):
    __tablename__ = "organization_patients"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), primary_key=True)
    patient_id: Mapped[UUID] = mapped_column(ForeignKey("patients.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    discharged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    organization: Mapped["Organization"] = relationship(back_populates="patients")
    patient: Mapped["Patient"] = relationship(back_populates="organizations")
