from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin

class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # TOTP secret
    transactional_consent: Mapped[bool] = mapped_column(Boolean, default=True)
    marketing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_consent: Mapped[bool] = mapped_column(Boolean, default=True)
    
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    memberships: Mapped[List["OrganizationMember"]] = relationship(back_populates="user")
    provider_profile: Mapped[Optional["Provider"]] = relationship(back_populates="user")
    staff_profile: Mapped[Optional["Staff"]] = relationship(back_populates="user")
    patient_profile: Mapped[Optional["Patient"]] = relationship(back_populates="user")
    proxy_profile: Mapped[Optional["Proxy"]] = relationship(back_populates="user")
    consents: Mapped[List["UserConsent"]] = relationship(back_populates="user")
    sessions: Mapped[List["UserSession"]] = relationship(back_populates="user")
    devices: Mapped[List["UserDevice"]] = relationship(back_populates="user")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")
    message_participations: Mapped[List["MessageParticipant"]] = relationship(back_populates="user")
    sent_messages: Mapped[List["Message"]] = relationship(back_populates="sender")
    calls: Mapped[List["Call"]] = relationship(back_populates="agent")
    assigned_tasks: Mapped[List["Task"]] = relationship(foreign_keys="[Task.assignee_id]", back_populates="assignee")
    created_tasks: Mapped[List["Task"]] = relationship(foreign_keys="[Task.created_by_id]", back_populates="created_by")
    support_tickets: Mapped[List["SupportTicket"]] = relationship(foreign_keys="[SupportTicket.user_id]", back_populates="user")