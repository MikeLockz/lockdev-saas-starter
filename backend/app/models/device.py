from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import TimestampMixin, pk_ulid

if TYPE_CHECKING:
    from app.models.user import User


class UserDevice(Base, TimestampMixin):
    __tablename__ = "user_devices"

    id: Mapped[pk_ulid]
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id"), index=True)
    fcm_token: Mapped[str] = mapped_column(String(255), index=True)
    device_name: Mapped[str | None] = mapped_column(String(100))
    platform: Mapped[str | None] = mapped_column(String(20))  # ios, android, web

    __table_args__ = (
        UniqueConstraint("user_id", "fcm_token", name="uix_user_device_token"),
    )

    user: Mapped["User"] = relationship()
