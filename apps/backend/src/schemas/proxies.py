"""Pydantic schemas for Proxy management."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ProxyPermissions(BaseModel):
    """All proxy permission flags."""

    can_view_profile: bool = True
    can_view_appointments: bool = True
    can_schedule_appointments: bool = False
    can_view_clinical_notes: bool = False
    can_view_billing: bool = False
    can_message_providers: bool = False


class ProxyAssignmentCreate(BaseModel):
    """Create a new proxy assignment."""

    email: EmailStr = Field(..., description="Email of user to grant proxy access")
    relationship_type: str = Field(..., description="Relationship: PARENT, SPOUSE, GUARDIAN, CAREGIVER, POA, OTHER")
    permissions: ProxyPermissions = Field(default_factory=ProxyPermissions)
    expires_at: datetime | None = Field(None, description="Optional expiration date")


class ProxyAssignmentUpdate(BaseModel):
    """Update proxy permissions."""

    permissions: ProxyPermissions | None = None
    expires_at: datetime | None = None


class ProxyUserInfo(BaseModel):
    """Embedded user information for proxy responses."""

    id: UUID
    email: str
    display_name: str | None = None


class ProxyAssignmentRead(BaseModel):
    """Read a proxy assignment with full details."""

    id: UUID
    proxy_id: UUID
    patient_id: UUID
    relationship_type: str

    # Permissions
    can_view_profile: bool
    can_view_appointments: bool
    can_schedule_appointments: bool
    can_view_clinical_notes: bool
    can_view_billing: bool
    can_message_providers: bool

    # Timestamps
    granted_at: datetime
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    # Nested user info
    user: ProxyUserInfo

    model_config = {"from_attributes": True}


class ProxyPatientInfo(BaseModel):
    """Patient info for proxy dashboard."""

    id: UUID
    first_name: str
    last_name: str
    dob: str
    medical_record_number: str | None = None


class ProxyPatientRead(BaseModel):
    """Patient with proxy permissions for proxy dashboard."""

    patient: ProxyPatientInfo
    relationship_type: str
    permissions: ProxyPermissions
    granted_at: datetime
    expires_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProxyListResponse(BaseModel):
    """List of proxies for a patient."""

    patient_id: UUID
    proxies: list[ProxyAssignmentRead]


class ProxyProfileRead(BaseModel):
    """Proxy profile for the current user."""

    id: UUID
    user_id: UUID
    relationship_to_patient: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
