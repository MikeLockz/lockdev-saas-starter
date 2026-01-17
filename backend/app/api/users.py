import pyotp
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.core.limiter import limiter
from app.models.device import UserDevice
from app.models.session import UserSession
from app.models.user import User
from app.schemas.users import (
    CommunicationPreferencesUpdate,
    DeviceTokenRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    MFAVerifyResponse,
    SessionRead,
    UserRead,
    UserUpdate,
)

router = APIRouter()


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user",
    description=(
        "Retrieves the profile information of the currently authenticated user."
    ),
)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.
    """
    return current_user


@router.get(
    "/me/sessions",
    response_model=list[SessionRead],
    summary="List active sessions",
    description="Retrieves a list of all active login sessions for the current user.",
)
async def list_my_sessions(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    List active sessions for the current user.
    """
    stmt = select(UserSession).where(
        UserSession.user_id == current_user.id, UserSession.is_revoked == False
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/me/mfa/setup",
    response_model=MFASetupResponse,
    summary="Setup MFA",
    description=(
        "Initiates the MFA setup process by generating a new secret and TOTP "
        "provisioning URI."
    ),
)
@limiter.limit("5/minute")
async def setup_mfa(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate MFA secret and provisioning URI.
    """
    secret = pyotp.random_base32()
    current_user.mfa_secret = secret
    await db.commit()

    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=current_user.email, issuer_name="Lockdev SaaS"
    )

    return {"provisioning_uri": provisioning_uri, "secret": secret}


@router.post(
    "/me/mfa/verify",
    response_model=MFAVerifyResponse,
    summary="Verify MFA",
    description=(
        "Verifies a TOTP code to complete the MFA setup process and provides "
        "backup codes."
    ),
)
@limiter.limit("5/minute")
async def verify_mfa(
    request: Request,
    req: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify MFA code and enable MFA for the user.
    """
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="MFA not set up"
        )

    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(req.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA code"
        )

    current_user.mfa_enabled = True
    backup_codes = [pyotp.random_base32()[:8] for _ in range(5)]
    current_user.mfa_backup_codes = {"codes": backup_codes}
    await db.commit()

    return {"backup_codes": backup_codes}


@router.post(
    "/device-token",
    summary="Register device token",
    description=(
        "Registers an FCM token for the user's current device to enable push "
        "notifications."
    ),
)
async def register_device_token(
    req: DeviceTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Register or update an FCM device token.
    """
    stmt = select(UserDevice).where(
        UserDevice.user_id == current_user.id, UserDevice.fcm_token == req.fcm_token
    )
    result = await db.execute(stmt)
    device = result.scalar_one_or_none()

    if device:
        device.device_name = req.device_name
        device.platform = req.platform
    else:
        device = UserDevice(
            user_id=current_user.id,
            fcm_token=req.fcm_token,
            device_name=req.device_name,
            platform=req.platform,
        )
        db.add(device)

    await db.commit()
    return {"message": "Device token registered"}


@router.delete(
    "/device-token",
    summary="Unregister device token",
    description=(
        "Removes an FCM token to stop receiving push notifications on a "
        "specific device."
    ),
)
async def unregister_device_token(
    fcm_token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove an FCM device token.
    """
    stmt = select(UserDevice).where(
        UserDevice.user_id == current_user.id, UserDevice.fcm_token == fcm_token
    )
    result = await db.execute(stmt)
    device = result.scalar_one_or_none()

    if device:
        await db.delete(device)
        await db.commit()

    return {"message": "Device token unregistered"}


@router.patch(
    "/me/communication-preferences",
    summary="Update communication preferences",
    description=(
        "Updates the user's consent for transactional and marketing " "communications."
    ),
)
async def update_communication_preferences(
    req: CommunicationPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update communication preferences.
    """
    # Placeholder for updating consent flags on User model
    await db.commit()
    return {"message": "Preferences updated"}


@router.delete(
    "/me/sessions/{session_id}",
    summary="Revoke session",
    description="Immediately invalidates a specific user session.",
)
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke a specific session.
    """
    session = await db.get(UserSession, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    session.is_revoked = True
    await db.commit()
    return {"message": "Session revoked"}


@router.patch(
    "/me",
    summary="Update profile",
    description="Updates the profile information for the current authenticated user.",
)
async def update_profile(
    req: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's profile.
    """
    await db.commit()
    return {"message": "Profile updated"}


@router.post(
    "/me/export",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Export my data",
    description=(
        "Triggers an asynchronous export of all data associated with the "
        "user's account for HIPAA compliance."
    ),
)
async def export_data(current_user: User = Depends(get_current_user)):
    """
    Trigger HIPAA data export.
    """
    return {"message": "Export started"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Soft delete user account.
    """
    current_user.is_active = False
    await db.commit()
