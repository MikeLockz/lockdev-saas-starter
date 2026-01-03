from typing import Optional, List
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
    status: Optional[str] = Field(None, description="OPEN, IN_PROGRESS, RESOLVED, CLOSED")
    priority: Optional[str] = None
    assigned_to_id: Optional[UUID] = None

class TicketRead(TicketBase):
    id: UUID
    user_id: UUID
    organization_id: Optional[UUID]
    status: str
    assigned_to_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    
    # We might want to include the last message or message count
    message_count: int = 0
    messages: List[SupportMessageRead] = []

    class Config:
        from_attributes = True
