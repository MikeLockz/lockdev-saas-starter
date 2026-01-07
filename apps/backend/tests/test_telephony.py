"""
Unit tests for Telephony Service (AWS Pinpoint and Amazon Connect).

Tests SMS sending, outbound calls, phone number masking, and error handling.
"""

from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import ClientError

from src.services.telephony import (
    initiate_outbound_call,
    mask_phone_number,
    send_sms,
    validate_phone_number,
)


def test_mask_phone_number_e164():
    """Test phone number masking with E.164 format."""
    assert mask_phone_number("+12125551234") == "+***-***-1234"
    assert mask_phone_number("+447911123456") == "+***-***-3456"


def test_mask_phone_number_national():
    """Test phone number masking with national format."""
    assert mask_phone_number("(212) 555-1234") == "***-***-1234"
    assert mask_phone_number("212-555-1234") == "***-***-1234"


def test_mask_phone_number_short():
    """Test phone number masking with short numbers."""
    assert mask_phone_number("123") == "***"
    assert mask_phone_number("12") == "***"


def test_validate_phone_number_valid():
    """Test phone number validation with valid E.164 numbers."""
    assert validate_phone_number("+12125551234") is True
    assert validate_phone_number("+447911123456") is True
    assert validate_phone_number("+861234567890") is True


def test_validate_phone_number_invalid():
    """Test phone number validation with invalid formats."""
    assert validate_phone_number("2125551234") is False  # Missing +
    assert validate_phone_number("+0125551234") is False  # Country code can't start with 0
    assert validate_phone_number("+1") is False  # Too short
    assert validate_phone_number("(212) 555-1234") is False  # Not E.164
    assert validate_phone_number("") is False  # Empty


@pytest.mark.asyncio
async def test_send_sms_success():
    """Test successful SMS sending with mocked Pinpoint."""
    mock_response = {
        "MessageResponse": {
            "Result": {
                "+12125551234": {
                    "MessageId": "test-message-id-123",
                    "DeliveryStatus": "SUCCESSFUL",
                }
            }
        }
    }

    mock_pinpoint = Mock()
    mock_pinpoint.send_messages = Mock(return_value=mock_response)

    with patch("src.services.telephony.boto3.client", return_value=mock_pinpoint):
        result = await send_sms("+12125551234", "Test message")

        assert result["message_id"] == "test-message-id-123"
        assert result["delivery_status"] == "SUCCESSFUL"
        assert result["to"] == "+***-***-1234"  # Masked

        # Verify the API was called correctly
        mock_pinpoint.send_messages.assert_called_once()
        call_args = mock_pinpoint.send_messages.call_args[1]
        assert call_args["MessageRequest"]["MessageConfiguration"]["SMSMessage"]["Body"] == "Test message"
        assert call_args["MessageRequest"]["MessageConfiguration"]["SMSMessage"]["MessageType"] == "TRANSACTIONAL"


@pytest.mark.asyncio
async def test_send_sms_with_user_id():
    """Test SMS sending with user_id for TCPA consent logging."""
    mock_response = {
        "MessageResponse": {
            "Result": {
                "+12125551234": {
                    "MessageId": "test-id",
                    "DeliveryStatus": "SUCCESSFUL",
                }
            }
        }
    }

    mock_pinpoint = Mock()
    mock_pinpoint.send_messages = Mock(return_value=mock_response)

    with patch("src.services.telephony.boto3.client", return_value=mock_pinpoint):
        result = await send_sms("+12125551234", "Test", user_id="user-123")

        assert result["message_id"] == "test-id"


@pytest.mark.asyncio
async def test_send_sms_empty_phone():
    """Test that empty phone number raises ValueError."""
    with pytest.raises(ValueError, match="Phone number cannot be empty"):
        await send_sms("", "Test message")

    with pytest.raises(ValueError, match="Phone number cannot be empty"):
        await send_sms("   ", "Test message")


@pytest.mark.asyncio
async def test_send_sms_invalid_phone():
    """Test that invalid phone number raises ValueError."""
    with pytest.raises(ValueError, match="Invalid phone number format"):
        await send_sms("2125551234", "Test message")  # Missing +

    with pytest.raises(ValueError, match="Invalid phone number format"):
        await send_sms("(212) 555-1234", "Test message")  # Not E.164


@pytest.mark.asyncio
async def test_send_sms_empty_body():
    """Test that empty message body raises ValueError."""
    with pytest.raises(ValueError, match="Message body cannot be empty"):
        await send_sms("+12125551234", "")

    with pytest.raises(ValueError, match="Message body cannot be empty"):
        await send_sms("+12125551234", "   ")


@pytest.mark.asyncio
async def test_send_sms_body_too_long():
    """Test that message body exceeding limit raises ValueError."""
    long_message = "a" * 1601  # Exceed 1600 char limit

    with pytest.raises(ValueError, match="Message body too long"):
        await send_sms("+12125551234", long_message)


@pytest.mark.asyncio
async def test_send_sms_api_error():
    """Test error handling when Pinpoint API fails."""
    mock_pinpoint = Mock()
    error_response = {
        "Error": {
            "Code": "ThrottlingException",
            "Message": "Rate exceeded",
        }
    }
    mock_pinpoint.send_messages = Mock(side_effect=ClientError(error_response, "SendMessages"))

    with patch("src.services.telephony.boto3.client", return_value=mock_pinpoint):
        with pytest.raises(RuntimeError, match="SMS send failed: ThrottlingException"):
            await send_sms("+12125551234", "Test message")


@pytest.mark.asyncio
async def test_initiate_outbound_call_success():
    """Test successful outbound call with mocked Amazon Connect."""
    mock_response = {
        "ContactId": "test-contact-id-456",
    }

    mock_connect = Mock()
    mock_connect.start_outbound_voice_contact = Mock(return_value=mock_response)

    with patch("src.services.telephony.boto3.client", return_value=mock_connect):
        result = await initiate_outbound_call("+12125551234", "flow-123")

        assert result["contact_id"] == "test-contact-id-456"
        assert result["to"] == "+***-***-1234"  # Masked
        assert result["status"] == "initiated"

        # Verify the API was called correctly
        mock_connect.start_outbound_voice_contact.assert_called_once()
        call_args = mock_connect.start_outbound_voice_contact.call_args[1]
        assert call_args["DestinationPhoneNumber"] == "+12125551234"
        assert call_args["ContactFlowId"] == "flow-123"


@pytest.mark.asyncio
async def test_initiate_outbound_call_empty_phone():
    """Test that empty phone number raises ValueError."""
    with pytest.raises(ValueError, match="Phone number cannot be empty"):
        await initiate_outbound_call("", "flow-123")


@pytest.mark.asyncio
async def test_initiate_outbound_call_invalid_phone():
    """Test that invalid phone number raises ValueError."""
    with pytest.raises(ValueError, match="Invalid phone number format"):
        await initiate_outbound_call("2125551234", "flow-123")


@pytest.mark.asyncio
async def test_initiate_outbound_call_no_flow_id():
    """Test that missing flow ID raises ValueError when no default is set."""
    with patch("src.services.telephony.settings.AWS_CONNECT_CONTACT_FLOW_ID", ""):
        with pytest.raises(ValueError, match="Contact flow ID is required"):
            await initiate_outbound_call("+12125551234")


@pytest.mark.asyncio
async def test_initiate_outbound_call_api_error():
    """Test error handling when Connect API fails."""
    mock_connect = Mock()
    error_response = {
        "Error": {
            "Code": "InvalidParameterException",
            "Message": "Invalid flow ID",
        }
    }
    mock_connect.start_outbound_voice_contact = Mock(
        side_effect=ClientError(error_response, "StartOutboundVoiceContact")
    )

    with patch("src.services.telephony.boto3.client", return_value=mock_connect):
        with pytest.raises(RuntimeError, match="Outbound call failed: InvalidParameterException"):
            await initiate_outbound_call("+12125551234", "invalid-flow")


@pytest.mark.asyncio
async def test_send_sms_unexpected_error():
    """Test error handling for unexpected exceptions."""
    mock_pinpoint = Mock()
    mock_pinpoint.send_messages = Mock(side_effect=Exception("Unexpected error"))

    with patch("src.services.telephony.boto3.client", return_value=mock_pinpoint):
        with pytest.raises(RuntimeError, match="SMS service error"):
            await send_sms("+12125551234", "Test")


@pytest.mark.asyncio
async def test_initiate_outbound_call_unexpected_error():
    """Test error handling for unexpected exceptions in calls."""
    mock_connect = Mock()
    mock_connect.start_outbound_voice_contact = Mock(side_effect=Exception("Unexpected error"))

    with patch("src.services.telephony.boto3.client", return_value=mock_connect):
        with pytest.raises(RuntimeError, match="Call service error"):
            await initiate_outbound_call("+12125551234", "flow-123")
