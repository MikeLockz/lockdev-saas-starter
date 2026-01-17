import datetime

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models_base import Base
from app.models.base import pk_ulid


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[pk_ulid]
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    actor_id: Mapped[str | None] = mapped_column(String(26), index=True)
    target_id: Mapped[str | None] = mapped_column(String(26), index=True)
    details: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
