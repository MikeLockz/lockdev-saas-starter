from datetime import datetime

from pydantic import BaseModel


class UserUpdate(BaseModel):
    display_name: str | None = None
    transactional_consent: bool | None = None
    marketing_consent: bool | None = None


class SessionRead(BaseModel):
    id: str
    device_info: dict | None
    created_at: datetime
    last_active_at: datetime | None
    is_revoked: bool

    class Config:
        from_attributes = True


class MFASetupResponse(BaseModel):
    provisioning_uri: str
    secret: str


class MFAVerifyRequest(BaseModel):
    code: str


class MFAVerifyResponse(BaseModel):
    backup_codes: list[str]


class DeviceTokenRequest(BaseModel):
    fcm_token: str
    device_name: str | None = None
    platform: str | None = None


class CommunicationPreferencesUpdate(BaseModel):
    transactional_consent: bool | None = None
    marketing_consent: bool | None = None
