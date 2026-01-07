"""
Telephony Service using AWS Pinpoint (SMS) and Amazon Connect (Calls).

This module provides SMS messaging and outbound calling capabilities with
HIPAA-compliant phone number masking.

Required Environment Variables:
    AWS_PINPOINT_APPLICATION_ID: Pinpoint application ID for SMS
    AWS_CONNECT_INSTANCE_ID: Amazon Connect instance ID
    AWS_CONNECT_CONTACT_FLOW_ID: Default contact flow ID for outbound calls
    AWS_ACCESS_KEY_ID: AWS credentials (via boto3 default chain)
    AWS_SECRET_ACCESS_KEY: AWS credentials (via boto3 default chain)

Required AWS Permissions:
    - mobiletargeting:SendMessages (Pinpoint)
    - connect:StartOutboundVoiceContact (Amazon Connect)
"""

import re

import boto3
import structlog
from botocore.exceptions import ClientError

from src.config import settings

logger = structlog.get_logger(__name__)


def mask_phone_number(phone: str) -> str:
    """
    Mask phone number for logging (HIPAA compliance).

    Args:
        phone: Phone number in any format

    Returns:
        Masked phone number showing only last 4 digits
        Example: +1***-***-1234
    """
    # Remove all non-digit characters except leading +
    digits_only = re.sub(r"[^\d+]", "", phone)

    # Extract last 4 digits
    if len(digits_only) < 4:
        return "***"

    last_four = digits_only[-4:]

    # Check if it starts with country code
    if digits_only.startswith("+"):
        return f"+***-***-{last_four}"
    else:
        return f"***-***-{last_four}"


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid E.164 format, False otherwise
    """
    # E.164 format: +[country code][number] (max 15 digits)
    pattern = r"^\+[1-9]\d{1,14}$"
    return bool(re.match(pattern, phone))


async def send_sms(to: str, body: str, user_id: str | None = None) -> dict:
    """
    Send SMS via AWS Pinpoint with TCPA consent check.

    Args:
        to: Recipient phone number in E.164 format (e.g., +12125551234)
        body: Message body (max 160 characters for single segment)
        user_id: Optional user ID for TCPA consent verification

    Returns:
        dict with message_id and delivery status

    Raises:
        ValueError: If phone number is invalid or body is empty
        RuntimeError: If AWS API call fails

    HIPAA Compliance:
        - Phone numbers are masked in all logs
        - No message content is logged

    TCPA Compliance:
        - If user_id is provided, consent should be verified (TODO: database integration)
        - If user_id is None, a warning is logged
    """
    # Validate inputs
    if not to or not to.strip():
        raise ValueError("Phone number cannot be empty")

    if not validate_phone_number(to):
        raise ValueError("Invalid phone number format. Expected E.164 format (e.g., +12125551234)")

    if not body or not body.strip():
        raise ValueError("Message body cannot be empty")

    if len(body) > 1600:  # AWS Pinpoint limit
        raise ValueError("Message body too long (max 1600 characters)")

    masked_phone = mask_phone_number(to)

    # TCPA Consent Check
    if user_id is None:
        logger.warning(
            "sms_sent_without_consent_check",
            to=masked_phone,
            message_length=len(body),
        )
    else:
        # TODO: Query database to check user.communication_consent_transactional
        # For now, just log that we would check
        logger.info(
            "sms_consent_check_required",
            user_id=user_id,
            to=masked_phone,
        )

    logger.info(
        "send_sms_requested",
        to=masked_phone,
        message_length=len(body),
        user_id=user_id,
    )

    try:
        # Initialize Pinpoint client
        pinpoint = boto3.client("pinpoint")

        # Send SMS
        response = pinpoint.send_messages(
            ApplicationId=settings.AWS_PINPOINT_APPLICATION_ID,
            MessageRequest={
                "Addresses": {
                    to: {
                        "ChannelType": "SMS",
                    }
                },
                "MessageConfiguration": {
                    "SMSMessage": {
                        "Body": body,
                        "MessageType": "TRANSACTIONAL",  # Not promotional
                    }
                },
            },
        )

        # Extract result
        result = response["MessageResponse"]["Result"][to]
        message_id = result.get("MessageId", "")
        delivery_status = result.get("DeliveryStatus", "UNKNOWN")

        logger.info(
            "send_sms_success",
            to=masked_phone,
            message_id=message_id,
            delivery_status=delivery_status,
        )

        return {
            "message_id": message_id,
            "delivery_status": delivery_status,
            "to": masked_phone,
        }

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        logger.error(
            "send_sms_failed",
            to=masked_phone,
            error_code=error_code,
            error_message=error_message,
        )

        raise RuntimeError(f"SMS send failed: {error_code} - {error_message}") from e
    except Exception as e:
        logger.error(
            "send_sms_unexpected_error",
            to=masked_phone,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise RuntimeError(f"SMS service error: {e}") from e


async def initiate_outbound_call(to: str, flow_id: str | None = None) -> dict:
    """
    Initiate outbound call via Amazon Connect.

    Args:
        to: Recipient phone number in E.164 format
        flow_id: Optional contact flow ID (uses default if not provided)

    Returns:
        dict with contact_id and status

    Raises:
        ValueError: If phone number is invalid
        RuntimeError: If AWS API call fails

    HIPAA Compliance:
        - Phone numbers are masked in all logs
    """
    # Validate phone number
    if not to or not to.strip():
        raise ValueError("Phone number cannot be empty")

    if not validate_phone_number(to):
        raise ValueError("Invalid phone number format. Expected E.164 format (e.g., +12125551234)")

    # Use default flow if not provided
    contact_flow_id = flow_id or settings.AWS_CONNECT_CONTACT_FLOW_ID

    if not contact_flow_id:
        raise ValueError("Contact flow ID is required (set AWS_CONNECT_CONTACT_FLOW_ID)")

    masked_phone = mask_phone_number(to)

    logger.info(
        "initiate_outbound_call_requested",
        to=masked_phone,
        flow_id=contact_flow_id,
    )

    try:
        # Initialize Connect client
        connect = boto3.client("connect")

        # Start outbound voice contact
        response = connect.start_outbound_voice_contact(
            DestinationPhoneNumber=to,
            ContactFlowId=contact_flow_id,
            InstanceId=settings.AWS_CONNECT_INSTANCE_ID,
        )

        contact_id = response.get("ContactId", "")

        logger.info(
            "initiate_outbound_call_success",
            to=masked_phone,
            contact_id=contact_id,
        )

        return {
            "contact_id": contact_id,
            "to": masked_phone,
            "status": "initiated",
        }

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        logger.error(
            "initiate_outbound_call_failed",
            to=masked_phone,
            error_code=error_code,
            error_message=error_message,
        )

        raise RuntimeError(f"Outbound call failed: {error_code} - {error_message}") from e
    except Exception as e:
        logger.error(
            "initiate_outbound_call_unexpected_error",
            to=masked_phone,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise RuntimeError(f"Call service error: {e}") from e
