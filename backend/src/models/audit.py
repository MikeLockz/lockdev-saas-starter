from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, UUID, INET
from .base import Base
from .mixins import UUIDMixin

class AuditLog(Base, UUIDMixin):
    __tablename__ = "audit_logs"

    actor_user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    organization_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("organizations.id"))
    
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    
    action_type: Mapped[str] = mapped_column(String(20), nullable=False) # READ, CREATE, UPDATE, DELETE
    ip_address: Mapped[Optional[str]] = mapped_column(INET)
    user_agent: Mapped[Optional[str]] = mapped_column(String)
    impersonator_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    
    changes_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
