from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import UUIDMixin

if TYPE_CHECKING:
    from .users import User


class UserDevice(Base, UUIDMixin):
    """
    Tracks FCM device tokens for push notifications.

    Used for:
    - Sending push notifications to user devices
    - Managing multiple devices per user
    - Tracking device platforms (iOS, Android, Web)
    """

    __tablename__ = "user_devices"
    __table_args__ = (UniqueConstraint("user_id", "fcm_token", name="uq_user_devices_user_token"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    fcm_token: Mapped[str] = mapped_column(String(512), nullable=False)
    device_name: Mapped[str | None] = mapped_column(String(255))
    platform: Mapped[str | None] = mapped_column(String(20))  # 'ios', 'android', 'web'
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="devices")
