from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.models.consent import ConsentDocument, UserConsent
from app.models.user import User

router = APIRouter()


class SignConsentRequest(BaseModel):
    document_id: str


@router.post("")
async def sign_consent(
    req: SignConsentRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify document exists
    doc = await db.get(ConsentDocument, req.document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # Check if already signed
    stmt = select(UserConsent).where(
        UserConsent.user_id == current_user.id, UserConsent.document_id == doc.id
    )
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        return {"message": "Consent already recorded"}

    # Create consent record
    consent = UserConsent(
        user_id=current_user.id,
        document_id=doc.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(consent)
    await db.commit()

    return {"message": "Consent recorded"}


async def verify_latest_consents(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Dependency to ensure user has signed the latest version of required documents.
    """
    required_types = ["TOS", "HIPAA"]

    for doc_type in required_types:
        # Get latest version of this document type
        stmt = (
            select(ConsentDocument)
            .where(ConsentDocument.type == doc_type)
            .order_by(ConsentDocument.version.desc())
            .limit(1)
        )

        result = await db.execute(stmt)
        latest_doc = result.scalar_one_or_none()

        if latest_doc:
            # Check if user has signed this specific document
            stmt = select(UserConsent).where(
                UserConsent.user_id == current_user.id,
                UserConsent.document_id == latest_doc.id,
            )
            consent_result = await db.execute(stmt)
            if not consent_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Consent required: {doc_type} (v{latest_doc.version})",
                )

    return True
