from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .base import TimestampSchema, UUIDSchema

# --- Call Schemas ---


class CallBase(BaseModel):
    direction: str = Field(..., description="INBOUND or OUTBOUND")
    phone_number: str = Field(..., description="Phone number associated with the call")
    notes: str | None = None
    outcome: str | None = None
    patient_id: UUID | None = None


class CallCreate(CallBase):
    pass


class CallUpdate(BaseModel):
    status: str | None = Field(None, description="QUEUED, IN_PROGRESS, COMPLETED, MISSED")
    notes: str | None = None
    outcome: str | None = None
    ended_at: datetime | None = None


class CallRead(CallBase, UUIDSchema, TimestampSchema):
    organization_id: UUID
    agent_id: UUID
    status: str
    started_at: datetime | None
    ended_at: datetime | None
    duration_seconds: int | None

    # We could include nested objects if needed, but keeping it flat for now
    agent_name: str | None = None
    patient_name: str | None = None


# --- Task Schemas ---


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    priority: str = Field(..., description="LOW, MEDIUM, HIGH, URGENT")
    due_date: date | None = None
    patient_id: UUID | None = None
    assignee_id: UUID


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = Field(None, description="TODO, IN_PROGRESS, DONE, CANCELLED")
    due_date: date | None = None
    assignee_id: UUID | None = None


class TaskRead(TaskBase, UUIDSchema, TimestampSchema):
    organization_id: UUID
    created_by_id: UUID
    status: str
    completed_at: datetime | None

    assignee_name: str | None = None
    patient_name: str | None = None
