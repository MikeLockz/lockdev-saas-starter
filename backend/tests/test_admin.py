from unittest.mock import patch

import pytest
from sqlalchemy import select

from app.core.auth import get_current_user, require_mfa
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
    app.dependency_overrides[require_mfa] = lambda: True

    # Mocking Firebase
    with patch("firebase_admin.auth.create_custom_token") as mock_token:
        mock_token.return_value = b"mocked_token"

        response = client.post(
            "/api/admin/impersonate/patient_123",
            json={"reason": "Emergency access for debugging"},
            headers={"Authorization": "Bearer fake-token"},
        )

        # Clean up override
        app.dependency_overrides.pop(get_current_user)
        app.dependency_overrides.pop(require_mfa)

        assert response.status_code == 200
        assert response.json()["custom_token"] == "mocked_token"

        # Verify Audit Log entry was created
        # Use scalar_one_or_none() to avoid MultipleResultsFound
        # if not cleaned up properly
        stmt = select(AuditLog)
        stmt = stmt.where(AuditLog.target_id == "patient_123")
        stmt = stmt.order_by(AuditLog.created_at.desc())
        result = await db.execute(stmt)
        # We might have logs from previous runs if cleanup failed.
        # But assuming we want to verify AT LEAST one exists.
        audit_log = result.scalars().first()
        assert audit_log is not None
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
    app.dependency_overrides[require_mfa] = lambda: True

    response = client.post(
        "/api/admin/impersonate/patient_123",
        json={"reason": "I want to see"},
        headers={"Authorization": "Bearer fake-token"},
    )

    app.dependency_overrides.pop(get_current_user)
    app.dependency_overrides.pop(require_mfa)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_impersonate_no_mfa_fails(client, db):
    # Even if admin, if MFA is missing, should fail
    admin = User(
        id="01KF2MBXMBE9PVGBM6MGP2SHMF", email="admin_nomfa@test.com", is_superuser=True
    )
    db.add(admin)
    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: admin

    # We DO NOT override require_mfa, but we override verify_token used by require_mfa?
    # require_mfa depends on verify_token.
    # verify_token returns dict.
    # We can override verify_token to return token WITHOUT 'amr'.

    from app.core.auth import verify_token

    app.dependency_overrides[verify_token] = lambda: {
        "email": "admin_nomfa@test.com",
        "amr": ["password"],
    }

    response = client.post(
        "/api/admin/impersonate/patient_123",
        json={"reason": "No MFA"},
        headers={"Authorization": "Bearer fake-token"},
    )

    app.dependency_overrides.pop(get_current_user)
    app.dependency_overrides.pop(verify_token)

    assert response.status_code == 403
    assert response.json()["detail"] == "MFA required for this action"
