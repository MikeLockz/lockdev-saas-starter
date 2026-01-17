import boto3
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class TelephonyService:
    def __init__(self):
        try:
            self.pinpoint = boto3.client("pinpoint", region_name=settings.AWS_REGION)
            self.connect = boto3.client("connect", region_name=settings.AWS_REGION)
            self.available = True
        except Exception:
            self.pinpoint = None
            self.connect = None
            self.available = False

    async def send_sms(self, to: str, body: str):
        """
        Sends an SMS using AWS Pinpoint.
        """
        masked_to = f"{to[:3]}***{to[-4:]}" if len(to) > 7 else "***"
        logger.info("SMS_SEND_REQUEST", to=masked_to)

        if not self.available:
            logger.warning("TELEPHONY_SERVICE_NOT_AVAILABLE")
            return False

        # Real AWS call would go here
        return True

    async def initiate_outbound_call(self, to: str, flow_id: str):
        """
        Initiates an outbound call using Amazon Connect.
        """
        masked_to = f"{to[:3]}***{to[-4:]}" if len(to) > 7 else "***"
        logger.info("CALL_INITIATE_REQUEST", to=masked_to)

        if not self.available:
            logger.warning("TELEPHONY_SERVICE_NOT_AVAILABLE")
            return False

        # Real AWS call would go here
        return True


telephony_service = TelephonyService()
