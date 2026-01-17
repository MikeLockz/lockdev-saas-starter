import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, pk_ulid

if TYPE_CHECKING:
    from app.models.contact import ContactMethod
    from app.models.user import User


class Provider(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "providers"

    id: Mapped[pk_ulid]
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id"), unique=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id"), index=True
    )
    npi: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    license_number: Mapped[str | None] = mapped_column(String(50))
    specialty: Mapped[str | None] = mapped_column(String(100))

    user: Mapped["User"] = relationship(back_populates="provider_profile")


class Staff(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "staff"

    id: Mapped[pk_ulid]
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id"), unique=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id"), index=True
    )
    job_title: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(100))

    user: Mapped["User"] = relationship(back_populates="staff_profile")


class Patient(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "patients"

    id: Mapped[pk_ulid]
    user_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id"), unique=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id"), index=True
    )

    first_name: Mapped[str] = mapped_column(String(100), index=True)
    last_name: Mapped[str] = mapped_column(String(100), index=True)
    mrn: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    dob: Mapped[datetime.date | None] = mapped_column(Date, index=True)
    gender: Mapped[str | None] = mapped_column(String(20))
    ssn_last_four: Mapped[str | None] = mapped_column(String(4))
    preferred_language: Mapped[str | None] = mapped_column(String(50), default="en")

    # Billing
    billing_manager_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id"), index=True
    )
    billing_manager_assigned_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    user: Mapped["User"] = relationship(
        back_populates="patient_profile", foreign_keys=[user_id]
    )
    billing_manager: Mapped["User"] = relationship(foreign_keys=[billing_manager_id])
    proxy_assignments: Mapped[list["PatientProxyAssignment"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )
    contact_methods: Mapped[list["ContactMethod"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "ix_patients_last_name_trgm",
            "last_name",
            postgresql_using="gin",
            postgresql_ops={"last_name": "gin_trgm_ops"},
        ),
    )


class Proxy(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "proxies"

    id: Mapped[pk_ulid]
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id"), unique=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id"), index=True
    )
    relationship_to_patient: Mapped[str | None] = mapped_column(String(50))

    user: Mapped["User"] = relationship()


class PatientProxyAssignment(Base, TimestampMixin):
    __tablename__ = "patient_proxy_assignments"

    id: Mapped[pk_ulid]
    patient_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("patients.id"), index=True
    )
    proxy_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("proxies.id"), index=True
    )
    access_level: Mapped[str] = mapped_column(String(20), default="full")

    patient: Mapped["Patient"] = relationship(back_populates="proxy_assignments")
    proxy: Mapped["Proxy"] = relationship()


# Event Listeners for Counter Maintenance
from sqlalchemy import event

from app.models.organization import Organization


@event.listens_for(Patient, "after_insert")
def increment_patient_count(mapper, connection, target):
    connection.execute(
        Organization.__table__.update()
        .where(Organization.id == target.organization_id)
        .values(patient_count=Organization.patient_count + 1)
    )


@event.listens_for(Patient, "after_delete")
def decrement_patient_count(mapper, connection, target):
    connection.execute(
        Organization.__table__.update()
        .where(Organization.id == target.organization_id)
        .values(patient_count=Organization.patient_count - 1)
    )
