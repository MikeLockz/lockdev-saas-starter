from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, IPvAnyAddress


class AuditLogBase(BaseModel):
    action_type: str = Field(..., description="Action performed (READ, CREATE, UPDATE, DELETE, etc.)")
    resource_type: str = Field(..., description="Type of resource effected (PATIENT, USER, etc.)")
    resource_id: UUID
    changes_json: dict[str, Any] | None = None


class AuditLogRead(AuditLogBase):
    id: UUID
    actor_user_id: UUID | None
    organization_id: UUID | None
    ip_address: IPvAnyAddress | str | None
    user_agent: str | None
    impersonator_id: UUID | None
    occurred_at: datetime

    class Config:
        from_attributes = True


class AuditLogSearchParams(BaseModel):
    action_type: str | None = None
    resource_type: str | None = None
    resource_id: UUID | None = None
    actor_user_id: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    page: int = 1
    page_size: int = 50
