from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.utils.npi import validate_npi

# =====================================================
# PROVIDER SCHEMAS
# =====================================================


class ProviderCreate(BaseModel):
    """Create a provider profile for a user."""

    user_id: UUID = Field(..., description="User to become a provider")
    npi_number: str | None = Field(None, max_length=10, description="National Provider Identifier")
    specialty: str | None = Field(None, max_length=100)
    license_number: str | None = Field(None, max_length=50)
    license_state: str | None = Field(None, max_length=2)
    dea_number: str | None = Field(None, max_length=20)

    @field_validator("npi_number")
    @classmethod
    def validate_npi_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not validate_npi(v):
            raise ValueError("Invalid NPI number. Must be 10 digits with valid Luhn checksum.")
        return v

    @field_validator("license_state")
    @classmethod
    def validate_state_code(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if len(v) != 2:
            raise ValueError("State code must be exactly 2 characters (e.g., 'CA')")
        return v.upper()


class ProviderUpdate(BaseModel):
    """Partial update for provider profile."""

    npi_number: str | None = Field(None, max_length=10)
    specialty: str | None = Field(None, max_length=100)
    license_number: str | None = Field(None, max_length=50)
    license_state: str | None = Field(None, max_length=2)
    dea_number: str | None = Field(None, max_length=20)
    is_active: bool | None = None

    @field_validator("npi_number")
    @classmethod
    def validate_npi_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not validate_npi(v):
            raise ValueError("Invalid NPI number. Must be 10 digits with valid Luhn checksum.")
        return v


class ProviderRead(BaseModel):
    """Full provider profile response."""

    id: UUID
    user_id: UUID
    organization_id: UUID
    npi_number: str | None
    specialty: str | None
    license_number: str | None
    license_state: str | None
    dea_number: str | None
    state_licenses: list[Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # User info (joined)
    user_email: str | None = None
    user_display_name: str | None = None

    model_config = {"from_attributes": True}


class ProviderListItem(BaseModel):
    """Compact provider for list views."""

    id: UUID
    user_id: UUID
    npi_number: str | None
    specialty: str | None
    is_active: bool
    user_email: str | None = None
    user_display_name: str | None = None

    model_config = {"from_attributes": True}


class PaginatedProviders(BaseModel):
    """Paginated provider list response."""

    items: list[ProviderListItem]
    total: int
    limit: int
    offset: int


# =====================================================
# STAFF SCHEMAS
# =====================================================


class StaffCreate(BaseModel):
    """Create a staff profile for a user."""

    user_id: UUID = Field(..., description="User to become staff")
    job_title: str | None = Field(None, max_length=100)
    department: str | None = Field(None, max_length=100)
    employee_id: str | None = Field(None, max_length=50)


class StaffUpdate(BaseModel):
    """Partial update for staff profile."""

    job_title: str | None = Field(None, max_length=100)
    department: str | None = Field(None, max_length=100)
    employee_id: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class StaffRead(BaseModel):
    """Full staff profile response."""

    id: UUID
    user_id: UUID
    organization_id: UUID
    job_title: str | None
    department: str | None
    employee_id: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # User info (joined)
    user_email: str | None = None
    user_display_name: str | None = None

    model_config = {"from_attributes": True}


class StaffListItem(BaseModel):
    """Compact staff for list views."""

    id: UUID
    user_id: UUID
    job_title: str | None
    department: str | None
    is_active: bool
    user_email: str | None = None
    user_display_name: str | None = None

    model_config = {"from_attributes": True}


class PaginatedStaff(BaseModel):
    """Paginated staff list response."""

    items: list[StaffListItem]
    total: int
    limit: int
    offset: int
