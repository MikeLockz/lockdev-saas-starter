import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import TimestampMixin, pk_ulid

if TYPE_CHECKING:
    from app.models.user import User


class UserSession(Base, TimestampMixin):
    __tablename__ = "user_sessions"

    id: Mapped[pk_ulid]
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id"), index=True)
    device_info: Mapped[dict | None] = mapped_column(JSON)
    firebase_uid: Mapped[str] = mapped_column(String(128), index=True)
    last_active_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=None, onupdate=None
    )
    expires_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship()
