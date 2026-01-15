"""
Support Ticket System.

This module provides a help desk ticketing system for user support requests,
with categorization, priority levels, and internal messaging.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDMixin


class SupportTicket(Base, UUIDMixin, TimestampMixin):
    """
    A user support request/ticket.

    Tickets track:
        - Category (TECHNICAL, BILLING, ACCOUNT, OTHER)
        - Priority (LOW, MEDIUM, HIGH)
        - Status (OPEN, IN_PROGRESS, RESOLVED, CLOSED)
        - Assignment to support staff
        - Resolution tracking
    """

    __tablename__ = "support_tickets"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )

    subject: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)  # TECHNICAL, BILLING, ACCOUNT, OTHER
    priority: Mapped[str] = mapped_column(String, nullable=False)  # LOW, MEDIUM, HIGH
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="OPEN", index=True
    )  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    assigned_to_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="support_tickets")
    organization = relationship("Organization")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    messages = relationship(
        "SupportMessage", back_populates="ticket", cascade="all, delete-orphan", order_by="SupportMessage.created_at"
    )


class SupportMessage(Base, UUIDMixin):
    """
    A message within a support ticket thread.

    Messages can be:
        - Public (visible to the user)
        - Internal (staff-only notes, hidden from user)
    """

    __tablename__ = "support_messages"

    ticket_id: Mapped[UUID] = mapped_column(
        ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )  # UUIDMixin doesn't have created_at, doing it manually or using TimestampMixin (but that adds updated_at too)

    # Relationships
    ticket = relationship("SupportTicket", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
