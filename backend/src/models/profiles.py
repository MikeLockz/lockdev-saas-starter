from datetime import date
from typing import Optional, List
from sqlalchemy import String, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from .base import Base
from .mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin

class Provider(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "providers"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    npi_number: Mapped[Optional[str]] = mapped_column(String(10), unique=True)
    dea_number: Mapped[Optional[str]] = mapped_column(String(20))
    specialty: Mapped[Optional[str]] = mapped_column(String(100))
    state_licenses: Mapped[list] = mapped_column(JSONB, default=[])

    user: Mapped["User"] = relationship(back_populates="provider_profile")

class Staff(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "staff"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    employee_id: Mapped[Optional[str]] = mapped_column(String(50))
    job_title: Mapped[Optional[str]] = mapped_column(String(100))

    user: Mapped["User"] = relationship(back_populates="staff_profile")

class Patient(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "patients"

    user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dob: Mapped[date] = mapped_column(Date, nullable=False)
    medical_record_number: Mapped[Optional[str]] = mapped_column(String(100))
    legal_sex: Mapped[Optional[str]] = mapped_column(String(20))
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(100))
    subscription_status: Mapped[str] = mapped_column(String(50), default="INCOMPLETE")

    user: Mapped[Optional["User"]] = relationship(back_populates="patient_profile")

    # Relationships
    organizations: Mapped[List["OrganizationPatient"]] = relationship(back_populates="patient")
    proxies: Mapped[List["PatientProxyAssignment"]] = relationship(back_populates="patient")

class Proxy(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "proxies"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    relationship_to_patient: Mapped[Optional[str]] = mapped_column(String(100))

    patients: Mapped[List["PatientProxyAssignment"]] = relationship(back_populates="proxy")
