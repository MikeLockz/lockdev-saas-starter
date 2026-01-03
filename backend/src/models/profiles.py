from datetime import date
from typing import Optional, List
from sqlalchemy import String, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from .base import Base
from .mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin

class Provider(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "providers"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    npi_number: Mapped[Optional[str]] = mapped_column(String(10))
    dea_number: Mapped[Optional[str]] = mapped_column(String(20))
    specialty: Mapped[Optional[str]] = mapped_column(String(100))
    license_number: Mapped[Optional[str]] = mapped_column(String(50))
    license_state: Mapped[Optional[str]] = mapped_column(String(2))
    state_licenses: Mapped[list] = mapped_column(JSONB, default=[])
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="provider_profile")
    organization: Mapped["Organization"] = relationship()
    care_team_assignments: Mapped[list["CareTeamAssignment"]] = relationship(back_populates="provider")

    # Unique NPI per organization constraint via index
    __table_args__ = (
        {"comment": "Provider profiles with NPI validation"},
    )


class Staff(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "staff"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    employee_id: Mapped[Optional[str]] = mapped_column(String(50))
    job_title: Mapped[Optional[str]] = mapped_column(String(100))
    department: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="staff_profile")
    organization: Mapped["Organization"] = relationship()

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
    contact_methods: Mapped[List["ContactMethod"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    message_threads: Mapped[List["MessageThread"]] = relationship(back_populates="patient")
    calls: Mapped[List["Call"]] = relationship(back_populates="patient")
    tasks: Mapped[List["Task"]] = relationship(back_populates="patient")

class Proxy(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """A user who manages care for one or more patients."""
    __tablename__ = "proxies"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    relationship_to_patient: Mapped[Optional[str]] = mapped_column(String(100))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="proxy_profile")
    patients: Mapped[List["PatientProxyAssignment"]] = relationship(back_populates="proxy")

