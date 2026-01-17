from datetime import datetime

from pydantic import BaseModel


class ContactMethodCreate(BaseModel):
    type: str
    value: str
    label: str | None = None
    is_primary: bool = False
    is_safe_for_voicemail: bool = False


class ContactMethodRead(BaseModel):
    id: str
    patient_id: str
    type: str
    value: str
    label: str | None
    is_primary: bool
    is_safe_for_voicemail: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ContactMethodUpdate(BaseModel):
    value: str | None = None
    label: str | None = None
    is_primary: bool | None = None
    is_safe_for_voicemail: bool | None = None
