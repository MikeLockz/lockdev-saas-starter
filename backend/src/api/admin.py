from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from firebase_admin import auth
import uuid

from src.database import get_db
from src.models import User, AuditLog
from src.security.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


class ImpersonationRequest(BaseModel):
    reason: str


async def require_admin(user: User = Depends(get_current_user)):
    if not user.is_super_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


@router.post("/impersonate/{patient_id}")
async def impersonate_patient(
    patient_id: str, req: ImpersonationRequest, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    try:
        pid = uuid.UUID(patient_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patient ID format")

    # Log Break Glass
    audit = AuditLog(
        actor_user_id=admin.id,
        action_type="IMPERSONATE",
        resource_type="PATIENT",
        resource_id=pid,
        changes_json={"reason": req.reason},
    )
    db.add(audit)
    await db.commit()

    # Generate Custom Token
    try:
        # Note: 'patient_id' here is expected to be the Firebase UID of the patient.
        # But our DB uses UUIDs.
        # If Patient User has a firebase_uid stored, we should use that.
        # But we don't have it in User model yet (I discussed this in 2.5).
        # For now, we assume the provided 'patient_id' IS the ID we want to impersonate.
        # If we use UUID as Firebase UID (custom auth), it works.

        additional_claims = {"act_as": str(pid), "impersonator_id": str(admin.id), "role": "PATIENT"}

        # We use the UUID as the uid for the token
        custom_token = auth.create_custom_token(str(pid), additional_claims)

        if isinstance(custom_token, bytes):
            custom_token = custom_token.decode("utf-8")

        return {"token": custom_token}
    except Exception as e:
        # If Firebase not init, this fails.
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")
