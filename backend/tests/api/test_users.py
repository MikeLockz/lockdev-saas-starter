import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.main import app
from app.models.user import User


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    uid = str(ULID())
    user = User(id=uid, email=f"me_{uid}@test.com")
    db.add(user)
    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.get("/api/users/me")
    assert response.status_code == 200
    assert response.json()["email"] == f"me_{uid}@test.com"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_my_sessions(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    uid = str(ULID())
    user = User(id=uid, email=f"sessions_{uid}@test.com")
    db.add(user)
    import datetime

    from app.models.session import UserSession

    session = UserSession(
        id=str(ULID()),
        user_id=user.id,
        firebase_uid=f"fb_{uid}",
        last_active_at=datetime.datetime.now(datetime.UTC),
    )
    db.add(session)
    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.get("/api/users/me/sessions")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_account(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    uid = str(ULID())
    user = User(id=uid, email=f"del_{uid}@test.com")
    db.add(user)
    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.delete("/api/users/me")
    assert response.status_code == 204

    # Check if soft deleted
    await db.refresh(user)
    assert user.is_active is False

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    uid = str(ULID())
    user = User(id=uid, email=f"upd_{uid}@test.com")
    db.add(user)
    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.patch("/api/users/me", json={"display_name": "New Name"})
    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_setup_mfa(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    uid = str(ULID())
    user = User(id=uid, email=f"mfa_{uid}@test.com")
    db.add(user)
    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.post("/api/users/me/mfa/setup")
    assert response.status_code == 200
    assert "provisioning_uri" in response.json()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_verify_mfa(client: AsyncClient, db: AsyncSession):
    import pyotp
    from ulid import ULID

    uid = str(ULID())
    secret = pyotp.random_base32()
    user = User(id=uid, email=f"v_mfa_{uid}@test.com", mfa_secret=secret)
    db.add(user)
    await db.flush()

    totp = pyotp.TOTP(secret)
    code = totp.now()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.post("/api/users/me/mfa/verify", json={"code": code})
    assert response.status_code == 200
    assert "backup_codes" in response.json()

    app.dependency_overrides.clear()
