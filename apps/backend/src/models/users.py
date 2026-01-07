from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)  # TOTP secret
    transactional_consent: Mapped[bool] = mapped_column(Boolean, default=True)
    marketing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_consent: Mapped[bool] = mapped_column(Boolean, default=True)

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    timezone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    memberships: Mapped[list["OrganizationMember"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    provider_profile: Mapped[Optional["Provider"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    staff_profile: Mapped[Optional["Staff"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    patient_profile: Mapped[Optional["Patient"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    proxy_profile: Mapped[Optional["Proxy"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    consents: Mapped[list["UserConsent"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list["UserSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    devices: Mapped[list["UserDevice"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    message_participations: Mapped[list["MessageParticipant"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    sent_messages: Mapped[list["Message"]] = relationship(back_populates="sender", cascade="all, delete-orphan")
    calls: Mapped[list["Call"]] = relationship(back_populates="agent", cascade="all, delete-orphan")
    assigned_tasks: Mapped[list["Task"]] = relationship(
        foreign_keys="[Task.assignee_id]", back_populates="assignee", cascade="all, delete-orphan"
    )
    created_tasks: Mapped[list["Task"]] = relationship(
        foreign_keys="[Task.created_by_id]", back_populates="created_by", cascade="all, delete-orphan"
    )
    support_tickets: Mapped[list["SupportTicket"]] = relationship(
        foreign_keys="[SupportTicket.user_id]", back_populates="user", cascade="all, delete-orphan"
    )
