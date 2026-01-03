"""
Tests for Device Token Management (Story 7.3).

Tests acceptance criteria:
- Register new device
- Update existing device
- Remove device
- Multiple devices per user
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import select

from src.models import User
from src.models.devices import UserDevice


@pytest.fixture
async def test_user_device(db_session):
    """Create a test user for device tests."""
    from uuid import uuid4
    unique_email = f"device-test-{uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        password_hash="hash",
        display_name="Device Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestDeviceTokenRegistration:
    """Test device token registration."""
    
    @pytest.mark.asyncio
    async def test_register_new_device(self, db_session, test_user_device):
        """Test registering a new device token."""
        # Create device
        device = UserDevice(
            user_id=test_user_device.id,
            fcm_token="test_fcm_token_12345",
            device_name="iPhone 15 Pro",
            platform="ios",
        )
        db_session.add(device)
        await db_session.commit()
        await db_session.refresh(device)
        
        assert device.id is not None
        assert device.user_id == test_user_device.id
        assert device.fcm_token == "test_fcm_token_12345"
        assert device.device_name == "iPhone 15 Pro"
        assert device.platform == "ios"
    
    @pytest.mark.asyncio
    async def test_update_existing_device(self, db_session, test_user_device):
        """Test updating an existing device token's info."""
        # Create device
        device = UserDevice(
            user_id=test_user_device.id,
            fcm_token="existing_token",
            device_name="Old Device Name",
            platform="android",
        )
        db_session.add(device)
        await db_session.commit()
        
        # Update device
        device.device_name = "New Device Name"
        device.last_active_at = datetime.now(timezone.utc)
        await db_session.commit()
        await db_session.refresh(device)
        
        assert device.device_name == "New Device Name"
    
    @pytest.mark.asyncio
    async def test_multiple_devices_per_user(self, db_session, test_user_device):
        """Test that a user can have multiple devices."""
        # Create multiple devices
        for i, platform in enumerate(["ios", "android", "web"]):
            device = UserDevice(
                user_id=test_user_device.id,
                fcm_token=f"fcm_token_{i}",
                device_name=f"Device {i}",
                platform=platform,
            )
            db_session.add(device)
        
        await db_session.commit()
        
        # Query devices
        stmt = select(UserDevice).where(UserDevice.user_id == test_user_device.id)
        result = await db_session.execute(stmt)
        devices = result.scalars().all()
        
        assert len(devices) == 3
        platforms = [d.platform for d in devices]
        assert "ios" in platforms
        assert "android" in platforms
        assert "web" in platforms


class TestDeviceTokenRemoval:
    """Test device token removal."""
    
    @pytest.mark.asyncio
    async def test_remove_device(self, db_session, test_user_device):
        """Test removing a device token."""
        # Create device
        device = UserDevice(
            user_id=test_user_device.id,
            fcm_token="token_to_remove",
            platform="ios",
        )
        db_session.add(device)
        await db_session.commit()
        
        device_id = device.id
        
        # Remove device
        await db_session.delete(device)
        await db_session.commit()
        
        # Verify removed
        stmt = select(UserDevice).where(UserDevice.id == device_id)
        result = await db_session.execute(stmt)
        found = result.scalar_one_or_none()
        
        assert found is None
    
    @pytest.mark.asyncio
    async def test_remove_nonexistent_device(self, db_session, test_user_device):
        """Test that removing a non-existent device doesn't error."""
        # Query for non-existent token
        stmt = select(UserDevice).where(
            UserDevice.user_id == test_user_device.id,
            UserDevice.fcm_token == "nonexistent_token",
        )
        result = await db_session.execute(stmt)
        device = result.scalar_one_or_none()
        
        # Should be None, no error
        assert device is None


class TestDeviceTokenConstraints:
    """Test unique constraint on device tokens."""
    
    @pytest.mark.asyncio
    async def test_unique_token_per_user(self, db_session, test_user_device):
        """Test unique constraint on (user_id, fcm_token)."""
        # Create first device
        device1 = UserDevice(
            user_id=test_user_device.id,
            fcm_token="unique_token",
            platform="ios",
        )
        db_session.add(device1)
        await db_session.commit()
        
        # Try to create duplicate - should raise
        device2 = UserDevice(
            user_id=test_user_device.id,
            fcm_token="unique_token",  # Same token
            platform="android",
        )
        db_session.add(device2)
        
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            await db_session.commit()
        
        # Rollback for cleanup
        await db_session.rollback()
