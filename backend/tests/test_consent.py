import pytest
from fastapi import HTTPException

from app.api.consent import verify_latest_consents
from app.models.consent import ConsentDocument, UserConsent
from app.models.user import User


@pytest.mark.asyncio
async def test_verify_consent_fails_when_missing(db):
    user = User(id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6Z1", email="consent1@test.com")
    db.add(user)

    doc = ConsentDocument(
        id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6Z2", type="TOS", version=1, content="Terms"
    )
    db.add(doc)
    await db.flush()

    with pytest.raises(HTTPException) as exc:
        await verify_latest_consents(current_user=user, db=db)
    assert exc.value.status_code == 403
    assert "Consent required" in exc.value.detail


@pytest.mark.asyncio
async def test_verify_consent_success_when_signed(db):
    user = User(id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6Z3", email="consent2@test.com")
    db.add(user)

    doc = ConsentDocument(
        id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6Z4", type="TOS", version=1, content="Terms"
    )
    db.add(doc)
    await db.flush()

    consent = UserConsent(user_id=user.id, document_id=doc.id)
    db.add(consent)
    await db.flush()

    result = await verify_latest_consents(current_user=user, db=db)
    assert result is True
