from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import TimestampMixin, pk_ulid

if TYPE_CHECKING:
    from app.models.user import User


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[pk_ulid]
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(
        String(50), default="INFO"
    )  # INFO, WARNING, APPOINTMENT
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    link: Mapped[str | None] = mapped_column(String(255))

    user: Mapped["User"] = relationship()
