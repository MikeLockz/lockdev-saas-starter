from unittest.mock import patch

import pytest
from sqlalchemy import select

from app.core.auth import get_current_user
from app.main import app
from app.models.audit import AuditLog
from app.models.user import User


@pytest.mark.asyncio
async def test_impersonate_admin_success(client, db):
    # Setup: Create an admin user in the DB
    admin = User(
        id="01KF2MBXMBE9PVGBM6MGP2SHVG", email="admin@test.com", is_superuser=True
    )
    db.add(admin)
    await db.flush()

    # Override dependency
    app.dependency_overrides[get_current_user] = lambda: admin

    # Mocking Firebase
    with patch("firebase_admin.auth.create_custom_token") as mock_token:
        mock_token.return_value = b"mocked_token"

        response = client.post(
            "/api/admin/impersonate/patient_123",
            json={"reason": "Emergency access for debugging"},
            headers={
                "Authorization": "Bearer fake-token"
            },  # Still need this to pass verify_token if it was a separate dep
        )

        # Clean up override
        app.dependency_overrides.pop(get_current_user)

        assert response.status_code == 200
        assert response.json()["custom_token"] == "mocked_token"

        # Verify Audit Log entry was created
        stmt = select(AuditLog).where(AuditLog.target_id == "patient_123")
        result = await db.execute(stmt)
        audit_log = result.scalar_one()
        assert audit_log.event_type == "BREAK_GLASS_IMPERSONATION"


@pytest.mark.asyncio
async def test_impersonate_non_admin_fails(client, db):
    # Setup: Create a regular user
    user = User(
        id="01KF2MBXMBE9PVGBM6MGP2SHXX", email="user@test.com", is_superuser=False
    )
    db.add(user)
    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.post(
        "/api/admin/impersonate/patient_123",
        json={"reason": "I want to see"},
        headers={"Authorization": "Bearer fake-token"},
    )

    app.dependency_overrides.pop(get_current_user)
    assert response.status_code == 403
