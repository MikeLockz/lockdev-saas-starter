from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AppointmentBase(BaseModel):
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=5, le=480)
    appointment_type: str = Field(default="FOLLOW_UP")
    reason: Optional[str] = None
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    patient_id: UUID
    provider_id: UUID


class AppointmentUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=5, le=480)
    appointment_type: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    status: str
    cancellation_reason: Optional[str] = None


class AppointmentRead(AppointmentBase):
    id: UUID
    organization_id: UUID
    patient_id: UUID
    provider_id: UUID
    status: str
    
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[UUID] = None
    cancellation_reason: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime

    # We will rely on loading these in the API logic or using a nested schema if we want full details.
    # For now, let's include basic info if available from the relationships.
    patient_name: Optional[str] = None
    provider_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
