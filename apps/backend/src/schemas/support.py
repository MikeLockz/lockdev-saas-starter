from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SupportMessageBase(BaseModel):
    body: str


class SupportMessageCreate(SupportMessageBase):
    is_internal: bool = False


class SupportMessageRead(SupportMessageBase):
    id: UUID
    ticket_id: UUID
    sender_id: UUID
    is_internal: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    subject: str
    category: str = Field(..., description="TECHNICAL, BILLING, ACCOUNT, OTHER")
    priority: str = Field(..., description="LOW, MEDIUM, HIGH")


class TicketCreate(TicketBase):
    initial_message: str


class TicketUpdate(BaseModel):
    status: str | None = Field(None, description="OPEN, IN_PROGRESS, RESOLVED, CLOSED")
    priority: str | None = None
    assigned_to_id: UUID | None = None


class TicketRead(TicketBase):
    id: UUID
    user_id: UUID
    organization_id: UUID | None
    status: str
    assigned_to_id: UUID | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None

    # We might want to include the last message or message count
    message_count: int = 0
    messages: list[SupportMessageRead] = []

    class Config:
        from_attributes = True
