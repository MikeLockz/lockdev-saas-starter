from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, List


class ContactMethodCreate(BaseModel):
    """Create a contact method for a patient."""
    type: str = Field(..., description="MOBILE, HOME, EMAIL")
    value: str = Field(..., description="The actual contact value")
    is_primary: bool = False
    is_safe_for_voicemail: bool = False  # HIPAA Critical
    label: Optional[str] = Field(None, description="Home, Work, Mobile")


class ContactMethodRead(BaseModel):
    """Read contact method with ID."""
    id: UUID
    type: str
    value: str
    is_primary: bool
    is_safe_for_voicemail: bool
    label: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatientCreate(BaseModel):
    """Create a patient. Will be enrolled in the organization."""
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    dob: date = Field(..., description="Date of birth")
    legal_sex: Optional[str] = Field(None, max_length=20)
    medical_record_number: Optional[str] = Field(None, max_length=100)
    contact_methods: Optional[List[ContactMethodCreate]] = None


class PatientUpdate(BaseModel):
    """Partial update for patient fields."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    dob: Optional[date] = None
    legal_sex: Optional[str] = Field(None, max_length=20)
    medical_record_number: Optional[str] = Field(None, max_length=100)


class PatientRead(BaseModel):
    """Full patient detail with contact methods."""
    id: UUID
    user_id: Optional[UUID]
    first_name: str
    last_name: str
    dob: date
    legal_sex: Optional[str]
    medical_record_number: Optional[str]
    stripe_customer_id: Optional[str]
    subscription_status: str
    contact_methods: List[ContactMethodRead] = []
    enrolled_at: Optional[datetime] = None  # From OrganizationPatient
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatientListItem(BaseModel):
    """Compact patient for list views."""
    id: UUID
    first_name: str
    last_name: str
    dob: date
    medical_record_number: Optional[str]
    enrolled_at: Optional[datetime] = None
    status: str = "ACTIVE"

    model_config = {"from_attributes": True}


class PatientSearchParams(BaseModel):
    """Search parameters for patients."""
    name: Optional[str] = Field(None, description="Search by name (fuzzy)")
    mrn: Optional[str] = Field(None, description="Search by MRN")
    dob: Optional[date] = Field(None, description="Filter by exact DOB")
    status: Optional[str] = Field(None, description="ACTIVE or DISCHARGED")
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class PaginatedPatients(BaseModel):
    """Paginated patient list response."""
    items: List[PatientListItem]
    total: int
    limit: int
    offset: int
