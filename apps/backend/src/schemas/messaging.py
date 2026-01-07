from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MessageBase(BaseModel):
    body: str


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: UUID
    thread_id: UUID
    sender_id: UUID | None
    created_at: datetime

    sender_name: str | None = None  # Populated from user relationship

    model_config = ConfigDict(from_attributes=True)


class ThreadBase(BaseModel):
    subject: str


class ThreadCreate(ThreadBase):
    organization_id: UUID
    patient_id: UUID | None = None
    initial_message: str
    participant_ids: list[UUID]  # List of User IDs to include


class ThreadRead(ThreadBase):
    id: UUID
    organization_id: UUID
    patient_id: UUID | None
    created_at: datetime
    updated_at: datetime

    last_message: MessageRead | None = None
    unread_count: int = 0
    participants: list["ParticipantRead"] = []

    model_config = ConfigDict(from_attributes=True)


class ThreadDetail(ThreadRead):
    messages: list[MessageRead] = []


class ParticipantRead(BaseModel):
    user_id: UUID
    joined_at: datetime
    last_read_at: datetime | None
    user_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ThreadListResponse(BaseModel):
    items: list[ThreadRead]
    total: int
    page: int
    size: int
