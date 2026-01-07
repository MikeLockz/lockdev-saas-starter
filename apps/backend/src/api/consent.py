from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import AuditLog, ConsentDocument, User, UserConsent
from src.security.auth import get_current_user

router = APIRouter(prefix="/consent", tags=["consent"])


class ConsentSignRequest(BaseModel):
    document_id: str


@router.get("/required")
async def get_required_consents(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    List all active consents and status for the current user.
    """
    result = await db.execute(select(ConsentDocument).where(ConsentDocument.is_active))
    active_docs = result.scalars().all()

    response = []
    for doc in active_docs:
        sig_result = await db.execute(
            select(UserConsent).where(UserConsent.user_id == user.id).where(UserConsent.document_id == doc.id)
        )
        sig = sig_result.scalar_one_or_none()
        response.append(
            {
                "id": doc.id,
                "type": doc.doc_type,
                "version": doc.version,
                "content_url": doc.content_url,
                "signed": sig is not None,
                "signed_at": sig.signed_at if sig else None,
            }
        )
    return response


@router.post("")
async def sign_consent(
    req: ConsentSignRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sign a specific consent document.
    """
    # Verify document exists and is active
    doc_result = await db.execute(select(ConsentDocument).where(ConsentDocument.id == req.document_id))
    doc = doc_result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not doc.is_active:
        raise HTTPException(status_code=400, detail="Document is no longer active")

    # Check if already signed
    existing_sig_result = await db.execute(
        select(UserConsent).where(UserConsent.user_id == user.id).where(UserConsent.document_id == req.document_id)
    )
    if existing_sig_result.scalar_one_or_none():
        return {"status": "already_signed"}

    # Sign
    ip = request.client.host
    user_agent = request.headers.get("user-agent")

    signature = UserConsent(user_id=user.id, document_id=doc.id, ip_address=ip, user_agent=user_agent)
    db.add(signature)

    # Audit Log
    audit = AuditLog(
        actor_user_id=user.id,
        action_type="CONSENT_AGREED",
        resource_type="CONSENT",
        resource_id=doc.id,
        changes_json={"version": doc.version, "ip": ip},
        ip_address=ip,
        user_agent=user_agent,
    )
    db.add(audit)

    await db.commit()
    return {"status": "signed"}
