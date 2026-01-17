import datetime
import secrets
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import TimestampMixin, pk_ulid

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


def generate_token():
    return secrets.token_urlsafe(32)


class Invitation(Base, TimestampMixin):
    __tablename__ = "invitations"

    id: Mapped[pk_ulid]
    organization_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id"), index=True
    )
    email: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[str] = mapped_column(String(50), default="member")
    token: Mapped[str] = mapped_column(String(128), unique=True, default=generate_token)
    invited_by_user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, accepted, expired

    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC)
        + datetime.timedelta(days=7),
    )
    accepted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    organization: Mapped["Organization"] = relationship()
    invited_by: Mapped["User"] = relationship()
