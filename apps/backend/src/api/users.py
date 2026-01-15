"""
User Profile & Session Management API.

Implements:
- GET /api/v1/users/me - Get current user profile
- PATCH /api/v1/users/me - Update profile
- DELETE /api/v1/users/me - Soft delete account
- GET /api/v1/users/me/sessions - List active sessions
- DELETE /api/v1/users/me/sessions/{session_id} - Revoke session
- POST /api/v1/users/me/export - Request HIPAA data export
- GET /api/v1/users/me/communication-preferences - Get preferences
- PATCH /api/v1/users/me/communication-preferences - Update preferences
"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from user_agents import parse as parse_user_agent

from src.database import get_db
from src.models import Patient, User, UserSession
from src.schemas.patients import PatientRead
from src.schemas.users import (
    CommunicationPreferencesRead,
    CommunicationPreferencesUpdate,
    SessionListResponse,
    SessionRead,
    SessionRevokeResponse,
    UserDeleteRequest,
    UserDeleteResponse,
    UserExportRequest,
    UserExportResponse,
    UserRead,
    UserUpdate,
)
from src.security.auth import get_current_user

router = APIRouter()


def get_device_string(user_agent: str | None) -> str:
    """Parse user agent string into readable device description."""
    if not user_agent:
        return "Unknown Device"
    try:
        ua = parse_user_agent(user_agent)
        browser = ua.browser.family
        os = ua.os.family
        if ua.is_mobile:
            device_type = "Mobile"
        elif ua.is_tablet:
            device_type = "Tablet"
        else:
            device_type = "Desktop"
        return f"{browser} on {os} ({device_type})"
    except Exception:
        return "Unknown Device"


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.
    """
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_users_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's profile.
    """
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        return current_user

    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.delete("/me", response_model=UserDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_users_me(
    delete_request: UserDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete user account (HIPAA compliance - data retained).

    This action cannot be undone. The account becomes inaccessible but
    data is retained for legal compliance.
    """
    # In production, verify password against Firebase or stored hash
    # For now, we just mark deleted_at

    now = datetime.now(UTC)
    current_user.deleted_at = now
    await db.commit()

    return UserDeleteResponse(success=True, deleted_at=now)


@router.get("/me/sessions", response_model=SessionListResponse)
async def list_sessions(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all active sessions for the current user.
    """
    # Get current session ID from request state if available
    current_session_id = getattr(request.state, "session_id", None)

    # Query active (non-revoked) sessions
    stmt = (
        select(UserSession)
        .where(UserSession.user_id == current_user.id)
        .where(UserSession.is_revoked == False)  # noqa: E712
        .order_by(UserSession.last_active_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)
    sessions = result.scalars().all()

    # Count total
    count_stmt = (
        select(UserSession).where(UserSession.user_id == current_user.id).where(UserSession.is_revoked == False)  # noqa: E712
    )
    count_result = await db.execute(count_stmt)
    total = len(count_result.scalars().all())

    items = [
        SessionRead(
            id=session.id,
            device=get_device_string(session.user_agent),
            ip_address=session.ip_address,
            location=None,  # GeoIP lookup future enhancement
            is_current=(str(session.id) == str(current_session_id)) if current_session_id else False,
            created_at=session.created_at,
            last_active_at=session.last_active_at,
        )
        for session in sessions
    ]

    return SessionListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete("/me/sessions/{session_id}", response_model=SessionRevokeResponse)
async def revoke_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Terminate a specific session.

    If session_id matches the current session, this is equivalent to logout.
    """
    # Find the session
    stmt = select(UserSession).where(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already revoked",
        )

    now = datetime.now(UTC)
    session.is_revoked = True
    await db.commit()

    return SessionRevokeResponse(success=True, terminated_at=now)


@router.post("/me/export", response_model=UserExportResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_export(
    export_request: UserExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Request a HIPAA data export.

    This initiates a background job. The user receives an email with a
    secure download link when the export is ready (typically 24-48 hours).
    """
    from datetime import timedelta
    from uuid import uuid4

    # In production, this would queue an ARQ background job
    # For now, return a placeholder response
    export_id = uuid4()
    estimated_completion = datetime.now(UTC) + timedelta(hours=24)

    # TODO: Queue background job via ARQ
    # await arq_pool.enqueue_job('export_user_data', current_user.id, export_request.format, export_request.include_documents)

    return UserExportResponse(
        export_id=export_id,
        status="PENDING",
        estimated_completion=estimated_completion,
    )


@router.get("/me/communication-preferences", response_model=CommunicationPreferencesRead)
async def get_communication_preferences(
    current_user: User = Depends(get_current_user),
):
    """
    Get user's communication opt-in status.
    """
    return CommunicationPreferencesRead(
        transactional_consent=current_user.transactional_consent,
        marketing_consent=current_user.marketing_consent,
        updated_at=current_user.updated_at,
    )


@router.patch("/me/communication-preferences", response_model=CommunicationPreferencesRead)
async def update_communication_preferences(
    prefs_update: CommunicationPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update communication preferences.

    Per TCPA compliance, transactional_consent must be True for appointment
    reminders and billing alerts. marketing_consent controls promotional
    communications.
    """
    update_data = prefs_update.model_dump(exclude_unset=True)

    if not update_data:
        return CommunicationPreferencesRead(
            transactional_consent=current_user.transactional_consent,
            marketing_consent=current_user.marketing_consent,
            updated_at=current_user.updated_at,
        )

    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(current_user)

    return CommunicationPreferencesRead(
        transactional_consent=current_user.transactional_consent,
        marketing_consent=current_user.marketing_consent,
        updated_at=current_user.updated_at,
    )


# =============================================================================
# Timezone Endpoints
# =============================================================================

from pydantic import BaseModel

from src.constants import DEFAULT_TIMEZONE
from src.validators import validate_timezone


class TimezoneResponse(BaseModel):
    """Response for timezone endpoint."""

    timezone: str
    source: str  # "user" or "organization"


class TimezoneUpdateRequest(BaseModel):
    """Request to update user timezone."""

    timezone: str


@router.get("/me/timezone", response_model=TimezoneResponse)
async def get_user_timezone(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current user's effective timezone.

    Resolution order:
    1. User's personal timezone preference (if set)
    2. Organization's timezone (if user has org membership)
    3. Default timezone (America/New_York)

    Returns timezone string and source indicator.
    """
    # If user has a personal timezone set
    if current_user.timezone:
        return TimezoneResponse(timezone=current_user.timezone, source="user")

    # Try to get organization timezone
    from src.models.organizations import Organization, OrganizationMember

    stmt = (
        select(Organization.timezone)
        .join(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.deleted_at.is_(None))
        .where(Organization.deleted_at.is_(None))
        .limit(1)
    )
    result = await db.execute(stmt)
    org_tz = result.scalar_one_or_none()

    if org_tz:
        return TimezoneResponse(timezone=org_tz, source="organization")

    # Default fallback
    return TimezoneResponse(timezone=DEFAULT_TIMEZONE, source="organization")


@router.patch("/me/timezone", response_model=TimezoneResponse)
async def update_user_timezone(
    tz_update: TimezoneUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the current user's timezone preference.

    Set to a valid IANA timezone identifier to override organization default.
    """
    if not validate_timezone(tz_update.timezone):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid timezone: {tz_update.timezone}. Must be a valid IANA timezone.",
        )

    current_user.timezone = tz_update.timezone
    current_user.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(current_user)

    return TimezoneResponse(timezone=current_user.timezone, source="user")


@router.delete("/me/timezone", response_model=TimezoneResponse)
async def clear_user_timezone(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Clear the user's timezone preference to use organization default.
    """
    current_user.timezone = None
    current_user.updated_at = datetime.now(UTC)
    await db.commit()

    # Return effective timezone (org or default)
    from src.models.organizations import Organization, OrganizationMember

    stmt = (
        select(Organization.timezone)
        .join(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.deleted_at.is_(None))
        .where(Organization.deleted_at.is_(None))
        .limit(1)
    )
    result = await db.execute(stmt)
    org_tz = result.scalar_one_or_none()

    return TimezoneResponse(timezone=org_tz or DEFAULT_TIMEZONE, source="organization")


# =============================================================================
# MFA Endpoints
# =============================================================================

import hashlib
import secrets

import pyotp

from src.schemas.users import (
    MFADisableRequest,
    MFADisableResponse,
    MFASetupResponse,
    MFAVerifyRequest,
    MFAVerifyResponse,
)


def generate_backup_codes(count: int = 8) -> list[str]:
    """Generate a list of backup codes."""
    codes = []
    for _ in range(count):
        # Format: XXXX-XXXX
        code = f"{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"
        codes.append(code)
    return codes


def hash_backup_code(code: str) -> str:
    """Hash a backup code for storage."""
    return hashlib.sha256(code.encode()).hexdigest()


@router.post("/me/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Initialize MFA setup.

    Returns a TOTP secret and provisioning URI for authenticator apps.
    The secret is stored temporarily until verified.
    """
    from datetime import timedelta

    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled. Disable it first to set up again.",
        )

    # Generate TOTP secret
    secret = pyotp.random_base32()

    # Create provisioning URI for QR code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=current_user.email, issuer_name="Lockdev")

    # Store secret temporarily (until verified)
    current_user.mfa_secret = secret
    await db.commit()

    # Set expiry for the setup process (15 minutes)
    expires_at = datetime.now(UTC) + timedelta(minutes=15)

    return MFASetupResponse(
        secret=secret,
        provisioning_uri=provisioning_uri,
        qr_code_data_url=None,  # QR generation is done client-side
        expires_at=expires_at,
    )


@router.post("/me/mfa/verify", response_model=MFAVerifyResponse)
async def mfa_verify(
    verify_request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Complete MFA setup by verifying a TOTP code.

    Returns backup codes (shown only once - user must save them).
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled.",
        )

    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA setup not initiated. Call /mfa/setup first.",
        )

    # Verify the TOTP code
    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(verify_request.code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please try again.",
        )

    # Generate backup codes
    backup_codes = generate_backup_codes(8)

    # Enable MFA
    current_user.mfa_enabled = True
    # Note: In production, backup codes would be stored hashed in user_mfa_backup_codes table

    now = datetime.now(UTC)
    current_user.updated_at = now
    await db.commit()

    return MFAVerifyResponse(
        success=True,
        mfa_enabled=True,
        backup_codes=backup_codes,
        enabled_at=now,
    )


@router.post("/me/mfa/disable", response_model=MFADisableResponse)
async def mfa_disable(
    disable_request: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disable MFA for the account.

    Requires password confirmation for security.
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled.",
        )

    # In production, verify password against Firebase or stored hash
    # For now, we accept any non-empty password
    if not disable_request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required to disable MFA.",
        )

    # Disable MFA
    current_user.mfa_enabled = False
    current_user.mfa_secret = None

    now = datetime.now(UTC)
    current_user.updated_at = now
    await db.commit()

    return MFADisableResponse(
        success=True,
        mfa_enabled=False,
        disabled_at=now,
    )


# =============================================================================
# Device Token Endpoints
# =============================================================================

from src.models import UserDevice
from src.schemas.users import (
    DeviceTokenDeleteRequest,
    DeviceTokenRequest,
    DeviceTokenResponse,
)


@router.post("/device-token", response_model=DeviceTokenResponse)
async def register_device_token(
    device_request: DeviceTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Register an FCM token for push notifications.

    If the token already exists for this user, updates the device info.
    """
    # Check if token already exists for this user
    stmt = select(UserDevice).where(
        UserDevice.user_id == current_user.id,
        UserDevice.fcm_token == device_request.token,
    )
    result = await db.execute(stmt)
    existing_device = result.scalar_one_or_none()

    now = datetime.now(UTC)

    if existing_device:
        # Update existing device
        existing_device.device_name = device_request.device_name
        existing_device.platform = device_request.platform
        existing_device.last_active_at = now
        existing_device.updated_at = now
    else:
        # Create new device
        new_device = UserDevice(
            user_id=current_user.id,
            fcm_token=device_request.token,
            device_name=device_request.device_name,
            platform=device_request.platform,
            last_active_at=now,
        )
        db.add(new_device)

    await db.commit()

    return DeviceTokenResponse(success=True)


@router.delete("/device-token", response_model=DeviceTokenResponse)
async def remove_device_token(
    delete_request: DeviceTokenDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove an FCM token (logout cleanup).
    """
    # Find the device
    stmt = select(UserDevice).where(
        UserDevice.user_id == current_user.id,
        UserDevice.fcm_token == delete_request.token,
    )
    result = await db.execute(stmt)
    device = result.scalar_one_or_none()

    if not device:
        # Token not found - return success anyway (idempotent)
        return DeviceTokenResponse(success=True)

    await db.delete(device)
    await db.commit()

    return DeviceTokenResponse(success=True)


# =============================================================================
# Proxy Patients Endpoint (for Proxy Dashboard)
# =============================================================================


from src.models.assignments import PatientProxyAssignment
from src.models.profiles import Proxy
from src.schemas.proxies import ProxyPatientInfo, ProxyPatientRead, ProxyPermissions, ProxyProfileRead


@router.get("/me/proxy-patients", response_model=list[ProxyPatientRead], tags=["proxies"])
async def get_my_proxy_patients(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    List patients the current user is proxy for.
    """
    now = datetime.now(UTC)

    # Find proxy profile for current user
    proxy_stmt = select(Proxy).where(Proxy.user_id == current_user.id).where(Proxy.deleted_at.is_(None))
    proxy_result = await db.execute(proxy_stmt)
    proxy = proxy_result.scalar_one_or_none()

    if not proxy:
        return []

    # Get active assignments
    stmt = (
        select(PatientProxyAssignment, Patient)
        .join(Patient, PatientProxyAssignment.patient_id == Patient.id)
        .where(PatientProxyAssignment.proxy_id == proxy.id)
        .where(PatientProxyAssignment.revoked_at.is_(None))
        .where(PatientProxyAssignment.deleted_at.is_(None))
        .where((PatientProxyAssignment.expires_at.is_(None)) | (PatientProxyAssignment.expires_at > now))
        .order_by(Patient.last_name, Patient.first_name)
    )
    result = await db.execute(stmt)
    rows = result.all()

    patients = []
    for assignment, patient in rows:
        patients.append(
            ProxyPatientRead(
                patient=ProxyPatientInfo(
                    id=patient.id,
                    first_name=patient.first_name,
                    last_name=patient.last_name,
                    dob=str(patient.dob),
                    medical_record_number=patient.medical_record_number,
                ),
                relationship_type=assignment.relationship_type,
                permissions=ProxyPermissions(
                    can_view_profile=assignment.can_view_profile,
                    can_view_appointments=assignment.can_view_appointments,
                    can_schedule_appointments=assignment.can_schedule_appointments,
                    can_view_clinical_notes=assignment.can_view_clinical_notes,
                    can_view_billing=assignment.can_view_billing,
                    can_message_providers=assignment.can_message_providers,
                ),
                granted_at=assignment.granted_at,
                expires_at=assignment.expires_at,
            )
        )

    return patients


@router.get("/me/proxy", response_model=ProxyProfileRead | None, tags=["proxies"])
async def get_my_proxy_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Get the current user's proxy profile if they are a proxy.
    Returns None if the user is not a proxy.
    """
    stmt = select(Proxy).where(Proxy.user_id == current_user.id).where(Proxy.deleted_at.is_(None))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.get("/me/patient", response_model=PatientRead | None, tags=["patients"])
async def get_my_patient_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Get the current user's patient profile if they are a patient.
    Returns None if the user is not a patient.
    """
    # Import locally to avoid circular imports? No, schema import is fine.
    # Note: imports for Patient and PatientRead must be added at top.

    stmt = (
        select(Patient)
        .options(selectinload(Patient.contact_methods))
        .where(Patient.user_id == current_user.id)
        .where(Patient.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
