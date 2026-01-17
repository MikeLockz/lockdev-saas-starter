import pytest

from app.core.auth import get_current_user
from app.main import app
from app.models.user import User


@pytest.mark.asyncio
async def test_hipaa_consent_missing_doc(client, db):
    # Setup user
    user = User(id="01KF2MBXMBE9PVGBM6MGP2SHUS", email="user_consent@test.com")
    db.add(user)
    await db.flush()

    # Override auth
    app.dependency_overrides[get_current_user] = lambda: user

    # Access protected route
    response = await client.post("/api/documents/upload-url?filename=test.pdf")

    app.dependency_overrides.pop(get_current_user)

    # Should fail with 503 because no HIPAA doc exists
    assert response.status_code == 503
    assert response.json()["detail"] == "HIPAA Consent Document not configured"
