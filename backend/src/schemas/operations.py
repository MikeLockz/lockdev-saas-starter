from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .base import UUIDSchema, TimestampSchema

# --- Call Schemas ---

class CallBase(BaseModel):
    direction: str = Field(..., description="INBOUND or OUTBOUND")
    phone_number: str = Field(..., description="Phone number associated with the call")
    notes: Optional[str] = None
    outcome: Optional[str] = None
    patient_id: Optional[UUID] = None

class CallCreate(CallBase):
    pass

class CallUpdate(BaseModel):
    status: Optional[str] = Field(None, description="QUEUED, IN_PROGRESS, COMPLETED, MISSED")
    notes: Optional[str] = None
    outcome: Optional[str] = None
    ended_at: Optional[datetime] = None

class CallRead(CallBase, UUIDSchema, TimestampSchema):
    organization_id: UUID
    agent_id: UUID
    status: str
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    
    # We could include nested objects if needed, but keeping it flat for now
    agent_name: Optional[str] = None 
    patient_name: Optional[str] = None

# --- Task Schemas ---

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = Field(..., description="LOW, MEDIUM, HIGH, URGENT")
    due_date: Optional[date] = None
    patient_id: Optional[UUID] = None
    assignee_id: UUID

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = Field(None, description="TODO, IN_PROGRESS, DONE, CANCELLED")
    due_date: Optional[date] = None
    assignee_id: Optional[UUID] = None

class TaskRead(TaskBase, UUIDSchema, TimestampSchema):
    organization_id: UUID
    created_by_id: UUID
    status: str
    completed_at: Optional[datetime]
    
    assignee_name: Optional[str] = None
    patient_name: Optional[str] = None
