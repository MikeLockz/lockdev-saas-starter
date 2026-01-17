from sqlalchemy import ForeignKey, Integer, String, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import TimestampMixin, pk_ulid


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[pk_ulid]
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Denormalized counters
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    patient_count: Mapped[int] = mapped_column(Integer, default=0)

    timezone: Mapped[str] = mapped_column(String(50), default="UTC")

    # Relationships
    members: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )


class OrganizationMember(Base, TimestampMixin):
    __tablename__ = "organization_members"

    id: Mapped[pk_ulid]
    organization_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id"), index=True
    )
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(
        String(50), default="member"
    )  # admin, member, etc.

    organization: Mapped["Organization"] = relationship(back_populates="members")


# Event Listeners for Counter Maintenance
@event.listens_for(OrganizationMember, "after_insert")
def increment_member_count(mapper, connection, target):
    connection.execute(
        Organization.__table__.update()
        .where(Organization.id == target.organization_id)
        .values(member_count=Organization.member_count + 1)
    )


@event.listens_for(OrganizationMember, "after_delete")
def decrement_member_count(mapper, connection, target):
    connection.execute(
        Organization.__table__.update()
        .where(Organization.id == target.organization_id)
        .values(member_count=Organization.member_count - 1)
    )
