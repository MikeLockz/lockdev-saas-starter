import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import TimestampMixin, pk_ulid

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.profile import Patient
    from app.models.user import User


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[pk_ulid]
    organization_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id"), index=True
    )
    assigned_to_user_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id"), index=True
    )
    patient_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("patients.id"), index=True
    )

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), default="TODO"
    )  # TODO, IN_PROGRESS, DONE
    priority: Mapped[str] = mapped_column(
        String(20), default="MEDIUM"
    )  # LOW, MEDIUM, HIGH, URGENT

    due_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))

    organization: Mapped["Organization"] = relationship()
    assigned_to: Mapped["User"] = relationship()
    patient: Mapped["Patient"] = relationship()


class CallLog(Base, TimestampMixin):
    __tablename__ = "call_logs"

    id: Mapped[pk_ulid]
    organization_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id"), index=True
    )
    agent_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id"), index=True
    )
    patient_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("patients.id"), index=True
    )

    direction: Mapped[str] = mapped_column(String(10))  # INBOUND, OUTBOUND
    status: Mapped[str] = mapped_column(String(20))  # CONNECTED, MISSED, VOICEMAIL
    duration_seconds: Mapped[int | None] = mapped_column(Integer)

    notes: Mapped[str | None] = mapped_column(Text)
    recording_url: Mapped[str | None] = mapped_column(String(512))

    organization: Mapped["Organization"] = relationship()
    agent: Mapped["User"] = relationship()
    patient: Mapped["Patient"] = relationship()
