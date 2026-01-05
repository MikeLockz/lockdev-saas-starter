from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=255)
    tax_id: Optional[str] = Field(None, max_length=50)
    settings_json: Dict[str, Any] = Field(default_factory=dict)
    timezone: str = Field(default="America/New_York", max_length=50)

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    tax_id: Optional[str] = Field(None, max_length=50)
    settings_json: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = Field(None, max_length=50)

class OrganizationRead(OrganizationBase):
    id: UUID
    stripe_customer_id: Optional[str]
    subscription_status: str
    is_active: bool
    member_count: int
    patient_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MemberRead(BaseModel):
    id: UUID
    user_id: UUID
    organization_id: UUID
    email: Optional[str] = None
    display_name: Optional[str] = None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class MemberInvite(BaseModel):
    email: str
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
