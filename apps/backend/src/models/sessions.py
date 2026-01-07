from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import UUIDMixin

if TYPE_CHECKING:
    from .users import User


class UserSession(Base, UUIDMixin):
    """
    Tracks active user sessions for security and audit purposes.

    Used for:
    - Displaying active sessions to users
    - Session revocation (logout from specific devices)
    - HIPAA session timeout compliance
    """

    __tablename__ = "user_sessions"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_info: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    firebase_uid: Mapped[str | None] = mapped_column(String(255))
    ip_address: Mapped[str | None] = mapped_column(String(45))  # IPv6 max
    user_agent: Mapped[str | None] = mapped_column(Text)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions")
