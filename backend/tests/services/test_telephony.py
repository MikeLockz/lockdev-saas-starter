import pytest

from app.services.telephony import telephony_service


@pytest.mark.asyncio
async def test_initiate_outbound_call_blocked_if_unsafe():
    """
    Verify that outbound calls are blocked if not safe for voicemail.
    """
    result = await telephony_service.initiate_outbound_call(
        "1234567890", "flow-123", safe_for_voicemail=False
    )
    assert result is False


@pytest.mark.asyncio
async def test_initiate_outbound_call_allowed_if_safe():
    """
    Verify that outbound calls are allowed if safe for voicemail.
    """
    # Force service to be available to test logic
    telephony_service.available = True

    result = await telephony_service.initiate_outbound_call(
        "1234567890", "flow-123", safe_for_voicemail=True
    )
    assert result is True
