import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.main import app
from app.models.organization import Organization, OrganizationMember
from app.models.profile import Patient
from app.models.user import User


@pytest.mark.asyncio
async def test_list_patients(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    from app.models.consent import ConsentDocument

    uid = str(ULID())
    user = User(id=uid, email=f"user_pat_{uid}@test.com")
    db.add(user)
    org_id = str(ULID())
    org = Organization(id=org_id, name="Pat Org", slug=f"pat-org-{org_id}")
    db.add(org)
    member = OrganizationMember(organization_id=org.id, user_id=user.id, role="admin")
    db.add(member)
    patient = Patient(
        id=str(ULID()),
        organization_id=org.id,
        first_name="John",
        last_name="Doe",
        mrn=f"MRN_{uid}",
    )
    db.add(patient)

    # Add ConsentDocument to satisfy require_hipaa_consent
    doc_id = str(ULID())
    doc = ConsentDocument(id=doc_id, type="HIPAA", version=1, content="HIPAA Content")
    db.add(doc)

    # Add UserConsent
    from app.models.consent import UserConsent

    user_consent = UserConsent(id=str(ULID()), user_id=user.id, document_id=doc_id)
    db.add(user_consent)

    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.get(f"/api/organizations/{org.id}/patients")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_patient(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    from app.models.consent import ConsentDocument, UserConsent

    uid = str(ULID())
    user = User(id=uid, email=f"user_get_pat_{uid}@test.com")
    db.add(user)
    org_id = str(ULID())
    org = Organization(id=org_id, name="Get Pat Org", slug=f"get-pat-org-{org_id}")
    db.add(org)
    member = OrganizationMember(organization_id=org.id, user_id=user.id, role="admin")
    db.add(member)
    pid = str(ULID())
    patient = Patient(
        id=pid,
        organization_id=org.id,
        first_name="Jane",
        last_name="Doe",
        mrn=f"MRN_GET_{uid}",
    )
    db.add(patient)

    doc_id = str(ULID())
    doc = ConsentDocument(id=doc_id, type="HIPAA", version=1, content="HIPAA Content")
    db.add(doc)
    user_consent = UserConsent(id=str(ULID()), user_id=user.id, document_id=doc_id)
    db.add(user_consent)

    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.get(f"/api/organizations/{org.id}/patients/{pid}")
    assert response.status_code == 200
    assert response.json()["first_name"] == "Jane"

    app.dependency_overrides.clear()
