"""
Multi-Tenant Organization Models.

This module defines the core multi-tenancy structure for healthcare organizations,
including membership management and patient enrollment.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin


class Organization(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    A healthcare organization (clinic, practice, hospital).

    Organizations are the primary tenant boundary for data isolation.
    Each organization has:
        - Subscription/billing via Stripe
        - Member users (Providers, Staff, Admins)
        - Enrolled patients
        - Configurable settings (timezone, preferences)
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_id: Mapped[str | None] = mapped_column(String(50))
    settings_json: Mapped[dict] = mapped_column(JSONB, default={})
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100))
    subscription_status: Mapped[str] = mapped_column(String(50), default="INCOMPLETE")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    timezone: Mapped[str] = mapped_column(String(50), default="America/New_York", nullable=False)

    member_count: Mapped[int] = mapped_column(Integer, default=0)
    patient_count: Mapped[int] = mapped_column(Integer, default=0)

    members: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    patients: Mapped[list["OrganizationPatient"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    message_threads: Mapped[list["MessageThread"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    calls: Mapped[list["Call"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="organization", cascade="all, delete-orphan")


class OrganizationMember(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Links a User to an Organization with a specific role.

    Roles determine access permissions:
        - ADMIN: Full organization management
        - PROVIDER: Clinical access
        - STAFF: Administrative access
    """

    __tablename__ = "organization_memberships"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # PROVIDER, STAFF, ADMIN

    organization: Mapped["Organization"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")

    __table_args__ = (UniqueConstraint("organization_id", "user_id"),)


class OrganizationPatient(Base):
    """
    Links a Patient to an Organization (enrollment).

    Tracks patient enrollment status and discharge dates.
    A patient can be enrolled in multiple organizations.
    """

    __tablename__ = "organization_patients"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), primary_key=True)
    patient_id: Mapped[UUID] = mapped_column(ForeignKey("patients.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")

    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    discharged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    organization: Mapped["Organization"] = relationship(back_populates="patients")
    patient: Mapped["Patient"] = relationship(back_populates="organizations")


# =============================================================================
# Counter Maintenance Event Listeners
# =============================================================================
# These SQLAlchemy event listeners automatically maintain the denormalized
# member_count and patient_count fields on Organization model.
# See: docs/implementation-plan/epic-08-organizations/story-08-05-counter-maintenance.md


from sqlalchemy import event


@event.listens_for(OrganizationMember, "after_insert")
def increment_member_count(mapper, connection, target):
    """Increment member_count when a new member is added."""
    connection.execute(
        Organization.__table__.update()
        .where(Organization.id == target.organization_id)
        .values(member_count=Organization.member_count + 1)
    )


@event.listens_for(OrganizationMember, "after_delete")
def decrement_member_count(mapper, connection, target):
    """Decrement member_count when a member is hard-deleted."""
    connection.execute(
        Organization.__table__.update()
        .where(Organization.id == target.organization_id)
        .values(member_count=Organization.member_count - 1)
    )


@event.listens_for(OrganizationMember, "after_update")
def handle_member_soft_delete(mapper, connection, target):
    """Handle soft-delete: decrement when deleted_at is set, increment when cleared."""
    from sqlalchemy import inspect

    state = inspect(target)
    deleted_at_history = state.attrs.deleted_at.history

    # Check if deleted_at changed
    if deleted_at_history.has_changes():
        old_value = deleted_at_history.deleted[0] if deleted_at_history.deleted else None
        new_value = deleted_at_history.added[0] if deleted_at_history.added else None

        if old_value is None and new_value is not None:
            # Soft delete: decrement count
            connection.execute(
                Organization.__table__.update()
                .where(Organization.id == target.organization_id)
                .values(member_count=Organization.member_count - 1)
            )
        elif old_value is not None and new_value is None:
            # Restore from soft delete: increment count
            connection.execute(
                Organization.__table__.update()
                .where(Organization.id == target.organization_id)
                .values(member_count=Organization.member_count + 1)
            )


@event.listens_for(OrganizationPatient, "after_insert")
def increment_patient_count(mapper, connection, target):
    """Increment patient_count when a patient is enrolled."""
    connection.execute(
        Organization.__table__.update()
        .where(Organization.id == target.organization_id)
        .values(patient_count=Organization.patient_count + 1)
    )


@event.listens_for(OrganizationPatient, "after_delete")
def decrement_patient_count(mapper, connection, target):
    """Decrement patient_count when a patient enrollment is deleted."""
    connection.execute(
        Organization.__table__.update()
        .where(Organization.id == target.organization_id)
        .values(patient_count=Organization.patient_count - 1)
    )
