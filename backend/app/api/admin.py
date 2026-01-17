from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.models.audit import AuditLog
from app.models.user import User

router = APIRouter()


class ImpersonateRequest(BaseModel):
    reason: str


@router.post("/impersonate/{patient_id}")
async def impersonate_patient(
    patient_id: str,
    req: ImpersonateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can impersonate"
        )

    # Log the event
    audit_entry = AuditLog(
        event_type="BREAK_GLASS_IMPERSONATION",
        actor_id=current_user.id,
        target_id=patient_id,
        details={"reason": req.reason},
    )
    db.add(audit_entry)
    await db.commit()

    # Generate Custom Token
    try:
        # Firebase custom tokens allow specifying custom claims
        custom_token = auth.create_custom_token(
            current_user.id,
            developer_claims={"act_as": patient_id, "impersonator_id": current_user.id},
        )
        # custom_token is bytes in newer versions of firebase-admin
        token_str = (
            custom_token.decode("utf-8")
            if isinstance(custom_token, bytes)
            else custom_token
        )
        return {"custom_token": token_str}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate token: {e!s}",
        )
