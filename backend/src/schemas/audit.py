from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, IPvAnyAddress

class AuditLogBase(BaseModel):
    action_type: str = Field(..., description="Action performed (READ, CREATE, UPDATE, DELETE, etc.)")
    resource_type: str = Field(..., description="Type of resource effected (PATIENT, USER, etc.)")
    resource_id: UUID
    changes_json: Optional[Dict[str, Any]] = None

class AuditLogRead(AuditLogBase):
    id: UUID
    actor_user_id: Optional[UUID]
    organization_id: Optional[UUID]
    ip_address: Optional[IPvAnyAddress | str]
    user_agent: Optional[str]
    impersonator_id: Optional[UUID]
    occurred_at: datetime

    class Config:
        from_attributes = True

class AuditLogSearchParams(BaseModel):
    action_type: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    actor_user_id: Optional[UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    page_size: int = 50
