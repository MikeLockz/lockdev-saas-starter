from datetime import date, datetime

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    first_name: str = Field(..., examples=["John"], description="Patient's given name")
    last_name: str = Field(..., examples=["Doe"], description="Patient's family name")
    mrn: str = Field(
        ..., examples=["MRN123456"], description="Medical Record Number (unique)"
    )
    dob: date | None = Field(None, examples=["1980-01-01"], description="Date of birth")
    gender: str | None = Field(None, examples=["male"], description="Biological gender")
    preferred_language: str | None = Field(
        "en", examples=["en"], description="ISO language code"
    )


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
