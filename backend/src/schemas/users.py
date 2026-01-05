from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class UserRead(BaseModel):
    """Full user profile response."""
    id: UUID
    email: EmailStr
    display_name: Optional[str] = None
    is_super_admin: bool = False
    mfa_enabled: bool = False
    requires_consent: bool = True
    transactional_consent: bool = True
    marketing_consent: bool = False
    timezone: Optional[str] = None
    effective_timezone: str = "America/New_York"  # Computed: user.timezone ?? org.timezone ?? DEFAULT
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Update user profile fields."""
    display_name: Optional[str] = Field(None, max_length=255)
    timezone: Optional[str] = Field(None, max_length=50)


class CommunicationPreferencesRead(BaseModel):
    """Communication preferences response."""
    transactional_consent: bool
    marketing_consent: bool
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommunicationPreferencesUpdate(BaseModel):
    """Update communication preferences."""
    transactional_consent: Optional[bool] = None
    marketing_consent: Optional[bool] = None


class SessionDeviceInfo(BaseModel):
    """Device information for a session."""
    user_agent: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    device_type: Optional[str] = None


class SessionRead(BaseModel):
    """Session information response."""
    id: UUID
    device: str  # Parsed from user_agent
    ip_address: Optional[str] = None
    location: Optional[str] = None  # GeoIP lookup (future)
    is_current: bool = False
    created_at: datetime
    last_active_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionListResponse(BaseModel):
    """Paginated list of sessions."""
    items: List[SessionRead]
    total: int
    limit: int = 50
    offset: int = 0


class SessionRevokeResponse(BaseModel):
    """Response after revoking a session."""
    success: bool = True
    terminated_at: datetime


class UserExportRequest(BaseModel):
    """Request body for HIPAA data export."""
    format: str = Field(default="json", pattern="^(json|pdf)$")
    include_documents: bool = False


class UserExportResponse(BaseModel):
    """Response after requesting data export."""
    export_id: UUID
    status: str = "PENDING"
    estimated_completion: datetime


class UserDeleteRequest(BaseModel):
    """Request body for account deletion."""
    password: str = Field(..., min_length=1)
    reason: Optional[str] = None


class UserDeleteResponse(BaseModel):
    """Response after account deletion."""
    success: bool = True
    deleted_at: datetime


# MFA Schemas
class MFASetupResponse(BaseModel):
    """Response for MFA setup initialization."""
    secret: str
    provisioning_uri: str
    qr_code_data_url: Optional[str] = None  # Base64 data URL for QR
    expires_at: datetime


class MFAVerifyRequest(BaseModel):
    """Request to verify MFA code and enable MFA."""
    code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$")


class MFAVerifyResponse(BaseModel):
    """Response after MFA verification."""
    success: bool = True
    mfa_enabled: bool = True
    backup_codes: List[str]
    enabled_at: datetime


class MFADisableRequest(BaseModel):
    """Request to disable MFA."""
    password: str = Field(..., min_length=1)


class MFADisableResponse(BaseModel):
    """Response after disabling MFA."""
    success: bool = True
    mfa_enabled: bool = False
    disabled_at: datetime


# Device Token Schemas
class DeviceTokenRequest(BaseModel):
    """Request to register a device token."""
    token: str = Field(..., min_length=1, max_length=512)
    platform: str = Field(..., pattern="^(ios|android|web)$")
    device_name: Optional[str] = Field(None, max_length=255)


class DeviceTokenResponse(BaseModel):
    """Response after registering device token."""
    success: bool = True


class DeviceTokenDeleteRequest(BaseModel):
    """Request to delete a device token."""
    token: str = Field(..., min_length=1, max_length=512)
