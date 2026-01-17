from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import TimestampMixin, pk_ulid


class SupportTicket(Base, TimestampMixin):
    __tablename__ = "support_tickets"

    id: Mapped[pk_ulid]
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id"), index=True)
    organization_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id"), index=True
    )

    subject: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), default="OPEN"
    )  # OPEN, IN_PROGRESS, CLOSED
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM")

    user: Mapped["User"] = relationship()
    organization: Mapped["Organization"] = relationship()
