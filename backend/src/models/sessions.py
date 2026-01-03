from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlalchemy import String, Boolean, Text, DateTime, ForeignKey
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

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    device_info: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    firebase_uid: Mapped[Optional[str]] = mapped_column(String(255))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 max
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions")
