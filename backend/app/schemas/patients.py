from datetime import date, datetime

from pydantic import BaseModel


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    mrn: str
    dob: date | None = None
    gender: str | None = None
    preferred_language: str | None = "en"


class PatientRead(BaseModel):
    id: str
    first_name: str
    last_name: str
    mrn: str
    dob: date | None
    gender: str | None
    preferred_language: str | None
    organization_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    dob: date | None = None
    gender: str | None = None
    preferred_language: str | None = None
