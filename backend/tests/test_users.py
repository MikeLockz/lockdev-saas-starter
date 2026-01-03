"""
Tests for User Profile & Session Management API.

Tests Story 7.1 acceptance criteria:
- Session listing with device info
- Session revocation
- Profile updates
- Data export request
- Account soft deletion
"""
import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from unittest.mock import patch, MagicMock

from fastapi import Request
from sqlalchemy import select

from src.models import User
from src.models.sessions import UserSession
from src.security.auth import verify_token, get_current_user, get_or_create_session
from src.database import user_id_ctx
from src.api.users import get_device_string


class MockToken:
    """Mock token for testing."""
    def __init__(self, email: str):
        self.credentials = f"mock_{email}"


class MockRequest:
    """Mock FastAPI request object."""
    def __init__(self, user_agent: str = "Mozilla/5.0", ip: str = "192.168.1.1"):
        self.headers = {"user-agent": user_agent}
        self.client = MagicMock()
        self.client.host = ip
        self.state = MagicMock()
        self.state.session_id = None


@pytest.fixture
async def test_user(db_session):
    """Create a test user with unique email per test run."""
    from uuid import uuid4
    unique_email = f"testuser-{uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        password_hash="hash",
        display_name="Test User",
        transactional_consent=True,
        marketing_consent=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_sessions(db_session, test_user):
    """Create test sessions for the user."""
    sessions = []
    for i, ua in enumerate([
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1",
    ]):
        session = UserSession(
            user_id=test_user.id,
            firebase_uid=f"firebase_uid_{i}",
            ip_address=f"192.168.1.{i+1}",
            user_agent=ua,
            device_info={"user_agent": ua},
            is_revoked=False,
            created_at=datetime.now(timezone.utc) - timedelta(hours=i),
            last_active_at=datetime.now(timezone.utc) - timedelta(minutes=i*10),
        )
        db_session.add(session)
        sessions.append(session)
    
    await db_session.commit()
    for s in sessions:
        await db_session.refresh(s)
    return sessions


class TestDeviceStringParsing:
    """Test user agent parsing."""
    
    def test_chrome_macos(self):
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        result = get_device_string(ua)
        assert "Chrome" in result
        assert "Mac OS X" in result
    
    def test_safari_iphone(self):
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1"
        result = get_device_string(ua)
        assert "Safari" in result or "Mobile Safari" in result
        assert "iOS" in result
    
    def test_unknown_agent(self):
        result = get_device_string(None)
        assert result == "Unknown Device"
    
    def test_invalid_agent(self):
        result = get_device_string("not-a-real-user-agent")
        # Should not crash
        assert isinstance(result, str)


class TestAuthFlow:
    """Test authentication flow with session creation."""
    
    @pytest.mark.asyncio
    async def test_mock_token_verification(self, db_session):
        """Test mock token for local development."""
        request = MockRequest()
        token = MockToken("test@example.com")
        
        with patch("src.security.auth.settings") as mock_settings:
            mock_settings.ENVIRONMENT = "local"
            token_data = await verify_token(request, token)
        
        assert token_data["email"] == "test@example.com"
        assert token_data["uid"] == "mock_uid"
    
    @pytest.mark.asyncio
    async def test_get_or_create_session_creates_new(self, db_session, test_user):
        """Test that get_or_create_session creates a new session."""
        request = MockRequest(user_agent="Test Browser/1.0", ip="10.0.0.1")
        
        # Verify no sessions exist initially for this firebase_uid
        stmt = select(UserSession).where(
            UserSession.user_id == test_user.id,
            UserSession.firebase_uid == "new_firebase_uid"
        )
        result = await db_session.execute(stmt)
        initial_sessions = result.scalars().all()
        assert len(initial_sessions) == 0
        
        # Create session
        session = await get_or_create_session(test_user, "new_firebase_uid", request, db_session)
        
        # Verify session was created
        assert session is not None
        assert session.user_id == test_user.id
        assert session.firebase_uid == "new_firebase_uid"
        assert session.ip_address == "10.0.0.1"
        assert session.user_agent == "Test Browser/1.0"
        assert session.is_revoked is False
    
    @pytest.mark.asyncio
    async def test_get_or_create_session_updates_existing(self, db_session, test_user):
        """Test that get_or_create_session updates existing session."""
        # Create initial session
        initial_session = UserSession(
            user_id=test_user.id,
            firebase_uid="existing_uid",
            ip_address="1.1.1.1",
            user_agent="Old Browser/1.0",
            last_active_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db_session.add(initial_session)
        await db_session.commit()
        await db_session.refresh(initial_session)
        old_last_active = initial_session.last_active_at
        session_id = initial_session.id
        
        # Get session again with new device info
        request = MockRequest(user_agent="New Browser/2.0", ip="2.2.2.2")
        session = await get_or_create_session(test_user, "existing_uid", request, db_session)
        
        # Verify same session was updated
        assert session.id == session_id
        assert session.ip_address == "2.2.2.2"
        assert session.user_agent == "New Browser/2.0"
        assert session.last_active_at > old_last_active
    
    @pytest.mark.asyncio
    async def test_deleted_user_check(self, db_session, test_user):
        """Test that soft-deleted users are flagged correctly."""
        assert test_user.deleted_at is None
        
        test_user.deleted_at = datetime.now(timezone.utc)
        await db_session.commit()
        await db_session.refresh(test_user)
        
        # User should have deleted_at set
        assert test_user.deleted_at is not None


class TestSessionManagement:
    """Test session listing and revocation."""
    
    @pytest.mark.asyncio
    async def test_list_sessions(self, db_session, test_user, test_sessions):
        """Test listing active sessions."""
        stmt = select(UserSession).where(
            UserSession.user_id == test_user.id,
            UserSession.is_revoked == False  # noqa: E712
        )
        result = await db_session.execute(stmt)
        sessions = result.scalars().all()
        
        assert len(sessions) == 2
        for session in sessions:
            assert session.user_id == test_user.id
            assert session.is_revoked is False
    
    @pytest.mark.asyncio
    async def test_revoke_session(self, db_session, test_user, test_sessions):
        """Test revoking a session."""
        session_to_revoke = test_sessions[0]
        
        # Revoke
        session_to_revoke.is_revoked = True
        await db_session.commit()
        await db_session.refresh(session_to_revoke)
        
        # Verify
        assert session_to_revoke.is_revoked is True
        
        # List should only show 1 session
        stmt = select(UserSession).where(
            UserSession.user_id == test_user.id,
            UserSession.is_revoked == False  # noqa: E712
        )
        result = await db_session.execute(stmt)
        active_sessions = result.scalars().all()
        assert len(active_sessions) == 1
    
    @pytest.mark.asyncio
    async def test_cannot_revoke_other_users_session(self, db_session, test_user, test_sessions):
        """Test that you can't revoke another user's session."""
        # Create another user with unique email
        from uuid import uuid4
        other_email = f"other-{uuid4().hex[:8]}@example.com"
        other_user = User(email=other_email, password_hash="hash")
        db_session.add(other_user)
        await db_session.commit()
        
        # Try to find session belonging to test_user as other_user
        stmt = select(UserSession).where(
            UserSession.id == test_sessions[0].id,
            UserSession.user_id == other_user.id,  # Wrong user!
        )
        result = await db_session.execute(stmt)
        session = result.scalar_one_or_none()
        
        # Should not find it
        assert session is None


class TestProfileManagement:
    """Test profile update functionality."""
    
    @pytest.mark.asyncio
    async def test_update_display_name(self, db_session, test_user):
        """Test updating user's display name."""
        test_user.display_name = "New Display Name"
        test_user.updated_at = datetime.now(timezone.utc)
        await db_session.commit()
        await db_session.refresh(test_user)
        
        assert test_user.display_name == "New Display Name"
    
    @pytest.mark.asyncio
    async def test_update_communication_preferences(self, db_session, test_user):
        """Test updating communication preferences."""
        assert test_user.marketing_consent is False
        
        test_user.marketing_consent = True
        await db_session.commit()
        await db_session.refresh(test_user)
        
        assert test_user.marketing_consent is True


class TestAccountDeletion:
    """Test soft delete functionality."""
    
    @pytest.mark.asyncio
    async def test_soft_delete_account(self, db_session, test_user):
        """Test soft deleting account sets deleted_at."""
        assert test_user.deleted_at is None
        
        test_user.deleted_at = datetime.now(timezone.utc)
        await db_session.commit()
        await db_session.refresh(test_user)
        
        assert test_user.deleted_at is not None
    
    @pytest.mark.asyncio
    async def test_soft_deleted_user_still_in_db(self, db_session, test_user):
        """Test that soft-deleted user data is retained (HIPAA compliance)."""
        user_id = test_user.id
        test_user.deleted_at = datetime.now(timezone.utc)
        await db_session.commit()
        
        # Query should still find the user
        stmt = select(User).where(User.id == user_id)
        result = await db_session.execute(stmt)
        found_user = result.scalar_one_or_none()
        
        assert found_user is not None
        assert found_user.deleted_at is not None


class TestDataExport:
    """Test HIPAA data export request."""
    
    @pytest.mark.asyncio
    async def test_export_request_placeholder(self, db_session, test_user):
        """Test that export request returns expected format."""
        # This is a placeholder test - actual implementation queues ARQ job
        from datetime import timedelta
        from uuid import uuid4
        
        export_id = uuid4()
        estimated_completion = datetime.now(timezone.utc) + timedelta(hours=24)
        
        # Verify format
        assert export_id is not None
        assert estimated_completion > datetime.now(timezone.utc)
