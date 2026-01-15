from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ContactMethodCreate(BaseModel):
    """Create a contact method for a patient."""

    type: str = Field(..., description="MOBILE, HOME, EMAIL")
    value: str = Field(..., description="The actual contact value")
    is_primary: bool = False
    is_safe_for_voicemail: bool = False  # HIPAA Critical
    label: str | None = Field(None, description="Home, Work, Mobile")


class ContactMethodRead(BaseModel):
    """Read contact method with ID."""

    id: UUID
    type: str
    value: str
    is_primary: bool
    is_safe_for_voicemail: bool
    label: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatientCreate(BaseModel):
    """Create a patient. Will be enrolled in the organization."""

    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    dob: date = Field(..., description="Date of birth")
    legal_sex: str | None = Field(None, max_length=20)
    medical_record_number: str | None = Field(None, max_length=100)
    contact_methods: list[ContactMethodCreate] | None = None


class PatientUpdate(BaseModel):
    """Partial update for patient fields."""

    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    dob: date | None = None
    legal_sex: str | None = Field(None, max_length=20)
    medical_record_number: str | None = Field(None, max_length=100)


class PatientRead(BaseModel):
    """Full patient detail with contact methods."""

    id: UUID
    user_id: UUID | None
    first_name: str
    last_name: str
    dob: date
    legal_sex: str | None
    medical_record_number: str | None
    stripe_customer_id: str | None
    subscription_status: str
    contact_methods: list[ContactMethodRead] = []
    enrolled_at: datetime | None = None  # From OrganizationPatient
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatientListItem(BaseModel):
    """Compact patient for list views."""

    id: UUID
    first_name: str
    last_name: str
    dob: date
    medical_record_number: str | None
    enrolled_at: datetime | None = None
    status: str = "ACTIVE"

    model_config = {"from_attributes": True}


class PatientSearchParams(BaseModel):
    """Search parameters for patients."""

    name: str | None = Field(None, description="Search by name (fuzzy)")
    mrn: str | None = Field(None, description="Search by MRN")
    dob: date | None = Field(None, description="Filter by exact DOB")
    status: str | None = Field(None, description="ACTIVE or DISCHARGED")
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class PaginatedPatients(BaseModel):
    """Paginated patient list response."""

    items: list[PatientListItem]
    total: int
    limit: int
    offset: int
