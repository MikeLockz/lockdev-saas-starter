"""
Communications Models

SQLAlchemy models for notifications and messaging system.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from src.models import User
    from src.models.organizations import Organization
    from src.models.profiles import Patient


class NotificationType(str, Enum):
    """Types of notifications."""

    APPOINTMENT = "APPOINTMENT"
    MESSAGE = "MESSAGE"
    SYSTEM = "SYSTEM"
    BILLING = "BILLING"


class Notification(Base):
    """User notification model."""

    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")


class MessageThread(Base):
    """Message thread/conversation model."""

    __tablename__ = "message_threads"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    patient_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="message_threads")
    patient: Mapped[Optional["Patient"]] = relationship("Patient", back_populates="message_threads")
    participants: Mapped[list["MessageParticipant"]] = relationship(
        "MessageParticipant", back_populates="thread", cascade="all, delete-orphan"
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="thread", cascade="all, delete-orphan", order_by="Message.created_at"
    )


class MessageParticipant(Base):
    """Message thread participant model."""

    __tablename__ = "message_participants"

    thread_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("message_threads.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    last_read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    thread: Mapped["MessageThread"] = relationship("MessageThread", back_populates="participants")
    user: Mapped["User"] = relationship("User", back_populates="message_participations")


class Message(Base):
    """Individual message in a thread."""

    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    thread_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("message_threads.id", ondelete="CASCADE"), nullable=False
    )
    sender_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    thread: Mapped["MessageThread"] = relationship("MessageThread", back_populates="messages")
    sender: Mapped[Optional["User"]] = relationship("User", back_populates="sent_messages")
