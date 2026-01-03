import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class InvitationBase(BaseModel):
    email: EmailStr
    role: str

class InvitationCreate(InvitationBase):
    pass

class InvitationRead(InvitationBase):
    id: uuid.UUID
    token: str
    status: str
    organization_id: uuid.UUID
    invited_by_user_id: uuid.UUID
    created_at: datetime
    expires_at: datetime
    accepted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
