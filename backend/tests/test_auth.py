import pytest
from fastapi import Request
from src.security.auth import verify_token, get_current_user
from src.models import User
from src.database import user_id_ctx

class MockToken:
    credentials = "mock_test@example.com"

@pytest.mark.asyncio
async def test_auth_flow(db_session):
    # Setup User
    user = User(email="test@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    
    # Verify Token (Mock)
    # We use our mock backdoor in verify_token
    request = Request(scope={"type": "http"})
    token_data = await verify_token(request, MockToken())
    assert token_data["email"] == "test@example.com"
    
    # Get Current User
    current_user = await get_current_user(token_data, db_session)
    assert current_user.id == user.id
    
    # Verify ContextVar
    assert user_id_ctx.get() == str(user.id)
