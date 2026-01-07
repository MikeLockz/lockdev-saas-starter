from unittest.mock import MagicMock

import pytest

from src.models import User
from src.security.auth import get_or_create_session, verify_token


class MockToken:
    credentials = "mock_test@example.com"


class MockRequest:
    """Mock FastAPI request object."""

    def __init__(self, user_agent: str = "Mozilla/5.0", ip: str = "192.168.1.1"):
        self.headers = {"user-agent": user_agent}
        self.client = MagicMock()
        self.client.host = ip
        self.state = MagicMock()
        self.state.session_id = None


@pytest.mark.asyncio
async def test_auth_flow(db_session):
    # Setup User with unique email
    from uuid import uuid4

    unique_email = f"auth-test-{uuid4().hex[:8]}@example.com"
    user = User(email=unique_email, password_hash="hash")
    db_session.add(user)
    await db_session.commit()

    # Verify Token (Mock)
    # We use our mock backdoor in verify_token
    request = MockRequest()
    token_data = await verify_token(request, MockToken())
    assert token_data["email"] == "test@example.com"

    # Test session creation
    session = await get_or_create_session(user, "test_firebase_uid", request, db_session)
    assert session is not None
    assert session.user_id == user.id
    assert session.firebase_uid == "test_firebase_uid"
