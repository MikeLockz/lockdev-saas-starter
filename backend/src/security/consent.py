from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.models import User, ConsentDocument, UserConsent
from src.security.auth import get_current_user

async def verify_latest_consents(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to check if the user has signed all active consent documents.
    If not, raises 403.
    """
    if user.is_super_admin:
        # Admins might bypass or have different rules, but usually they also need TOS.
        # For now, enforce for everyone.
        pass

    # 1. Get all active documents
    result = await db.execute(select(ConsentDocument).where(ConsentDocument.is_active == True))
    active_docs = result.scalars().all()

    if not active_docs:
        return user

    # 2. Get user's signatures for these docs
    active_doc_ids = [d.id for d in active_docs]
    
    # We want to check if there is a signature for each active document
    # A more efficient query might be to join, but simple check is okay for few docs.
    
    user_signatures_result = await db.execute(
        select(UserConsent)
        .where(UserConsent.user_id == user.id)
        .where(UserConsent.document_id.in_(active_doc_ids))
    )
    user_signatures = user_signatures_result.scalars().all()
    signed_doc_ids = {s.document_id for s in user_signatures}
    
    missing_docs = []
    for doc in active_docs:
        if doc.id not in signed_doc_ids:
            missing_docs.append(doc)
            
    if missing_docs:
        raise HTTPException(
            status_code=403, 
            detail="Consent Required",
            headers={"X-Missing-Consents": ",".join([d.doc_type for d in missing_docs])}
        )
        
    return user
