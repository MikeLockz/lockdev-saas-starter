from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AppointmentBase(BaseModel):
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=5, le=480)
    appointment_type: str = Field(default="FOLLOW_UP")
    reason: str | None = None
    notes: str | None = None


class AppointmentCreate(AppointmentBase):
    patient_id: UUID
    provider_id: UUID


class AppointmentUpdate(BaseModel):
    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, ge=5, le=480)
    appointment_type: str | None = None
    reason: str | None = None
    notes: str | None = None


class AppointmentStatusUpdate(BaseModel):
    status: str
    cancellation_reason: str | None = None


class AppointmentRead(AppointmentBase):
    id: UUID
    organization_id: UUID
    patient_id: UUID
    provider_id: UUID
    status: str

    cancelled_at: datetime | None = None
    cancelled_by: UUID | None = None
    cancellation_reason: str | None = None

    created_at: datetime
    updated_at: datetime

    # We will rely on loading these in the API logic or using a nested schema if we want full details.
    # For now, let's include basic info if available from the relationships.
    patient_name: str | None = None
    provider_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
