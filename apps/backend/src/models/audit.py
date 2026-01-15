"""
Audit Logging for HIPAA Compliance.

This module provides immutable audit trail records for all PHI access
and modifications, required for HIPAA Security Rule compliance.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import UUIDMixin


class AuditLog(Base, UUIDMixin):
    """
    Immutable audit trail record for tracking PHI access and changes.

    Every read, create, update, or delete of protected health information
    is logged with:
        - Actor (user who performed the action)
        - Resource (what was accessed/modified)
        - Action type (READ, CREATE, UPDATE, DELETE)
        - Client metadata (IP address, user agent)
        - Impersonator tracking (if action was performed on behalf of another user)

    These records should NEVER be deleted or modified after creation.
    """

    __tablename__ = "audit_logs"

    actor_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    organization_id: Mapped[UUID | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"))

    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    action_type: Mapped[str] = mapped_column(String(20), nullable=False)  # READ, CREATE, UPDATE, DELETE
    ip_address: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(String)
    impersonator_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    changes_json: Mapped[dict | None] = mapped_column(JSONB)

    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
