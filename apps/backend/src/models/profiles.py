"""User Profile Models for Healthcare Roles.

This module defines role-specific profiles that extend the base User model:
- Provider: Licensed healthcare professionals (doctors, nurses)
- Staff: Administrative and support personnel
- Patient: Individuals receiving care
- Proxy: Users managing care for patients (parents, caregivers)
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin


class Provider(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    A licensed healthcare provider (doctor, nurse, therapist, etc.).

    Stores professional credentials including:
        - NPI (National Provider Identifier)
        - DEA number for prescribing
        - State medical license information
        - Specialty designation
    """

    __tablename__ = "providers"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    npi_number: Mapped[str | None] = mapped_column(String(10))
    dea_number: Mapped[str | None] = mapped_column(String(20))
    specialty: Mapped[str | None] = mapped_column(String(100))
    license_number: Mapped[str | None] = mapped_column(String(50))
    license_state: Mapped[str | None] = mapped_column(String(2))
    state_licenses: Mapped[list] = mapped_column(JSONB, default=[])
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="provider_profile")
    organization: Mapped["Organization"] = relationship()
    care_team_assignments: Mapped[list["CareTeamAssignment"]] = relationship(back_populates="provider")

    # Unique NPI per organization constraint via partial index
    __table_args__ = (
        Index(
            "ix_providers_org_npi_unique",
            "organization_id",
            "npi_number",
            unique=True,
            postgresql_where="npi_number IS NOT NULL",
        ),
        {"comment": "Provider profiles with NPI validation"},
    )


class Staff(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Administrative or support staff member.

    Staff do not have clinical credentials but may have access to:
        - Patient scheduling
        - Billing operations
        - Administrative functions
    """

    __tablename__ = "staff"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    employee_id: Mapped[str | None] = mapped_column(String(50))
    job_title: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="staff_profile")
    organization: Mapped["Organization"] = relationship()


class Patient(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    A patient receiving healthcare services.

    Contains PHI (Protected Health Information) including:
        - Demographics (name, DOB, legal sex)
        - Medical record number
        - Billing/subscription status
        - Billing manager assignment for proxy billing

    NOTE: user_id may be NULL if the patient portal is not activated.
    """

    __tablename__ = "patients"

    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dob: Mapped[date] = mapped_column(Date, nullable=False)
    medical_record_number: Mapped[str | None] = mapped_column(String(100))
    legal_sex: Mapped[str | None] = mapped_column(String(20))
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100))
    subscription_status: Mapped[str] = mapped_column(String(50), default="INCOMPLETE")

    # Billing Manager fields (Epic 22)
    billing_manager_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    billing_manager_assigned_at: Mapped[datetime | None]
    billing_manager_assigned_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    user: Mapped[Optional["User"]] = relationship(back_populates="patient_profile", foreign_keys=[user_id])
    billing_manager: Mapped[Optional["User"]] = relationship(foreign_keys=[billing_manager_id], lazy="joined")
    billing_manager_assigner: Mapped[Optional["User"]] = relationship(foreign_keys=[billing_manager_assigned_by])

    # Relationships
    organizations: Mapped[list["OrganizationPatient"]] = relationship(back_populates="patient")
    proxies: Mapped[list["PatientProxyAssignment"]] = relationship(back_populates="patient")
    contact_methods: Mapped[list["ContactMethod"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    message_threads: Mapped[list["MessageThread"]] = relationship(back_populates="patient")
    calls: Mapped[list["Call"]] = relationship(back_populates="patient")
    tasks: Mapped[list["Task"]] = relationship(back_populates="patient")


class Proxy(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """A user who manages care for one or more patients."""

    __tablename__ = "proxies"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    relationship_to_patient: Mapped[str | None] = mapped_column(String(100))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="proxy_profile")
    patients: Mapped[list["PatientProxyAssignment"]] = relationship(back_populates="proxy")
