import logging
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.profiles import Patient
from src.services.billing_access import get_billing_email_recipient

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        base_dir = Path(__file__).parent.parent
        self.template_dir = base_dir / "templates"
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))

    async def send_email(self, to_email: str, subject: str, html_content: str, attachments: list = None):
        """
        Send email. Currently MOCKED.
        """
        logger.info(f"MOCK EMAIL SEND: To={to_email}, Subject={subject}")
        # In a real impl, use aiosmtplib or boto3 SES
        if attachments:
            logger.info(f"Email has {len(attachments)} attachments")

        # Log content for debug
        # logger.debug(html_content)
        return True

    async def send_payment_success_email(
        self,
        db: AsyncSession,
        patient: Patient,
        amount_cents: int,
        receipt_number: str,
        payment_date: datetime,
        payment_method: str,
        plan_name: str,
        billing_period: str,
        receipt_url: str,
        pdf_attachment: bytes,
    ):
        if not settings.ENABLE_BILLING_EMAILS:
            return

        recipient_email, recipient_name = await get_billing_email_recipient(db, patient)

        template = self.env.get_template("emails/billing/payment-success.html")

        # Determine actual patient name for template logic
        actual_patient_name = f"{patient.first_name} {patient.last_name}"
        is_proxy_managed = patient.billing_manager_id is not None

        html_content = template.render(
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            actual_patient_name=actual_patient_name,
            is_proxy_managed=is_proxy_managed,
            amount_dollars=f"{amount_cents / 100:.2f}",
            receipt_number=receipt_number,
            payment_date=payment_date.strftime("%B %d, %Y"),
            payment_method=payment_method,
            plan_name=plan_name,
            billing_period=billing_period,
            receipt_url=receipt_url,
            company_name=settings.COMPANY_NAME,
            patient_email=recipient_email,  # needed for footer
        )

        await self.send_email(
            to_email=recipient_email,
            subject=f"Payment Successful - Receipt {receipt_number}",
            html_content=html_content,
            attachments=[
                {
                    "filename": f"receipt-{receipt_number}.pdf",
                    "content": pdf_attachment,
                    "content_type": "application/pdf",
                }
            ],
        )

    async def send_payment_failed_email(
        self,
        db: AsyncSession,
        patient: Patient,
        amount_cents: int,
        failure_reason: str,
        attempt_count: int,
        update_payment_url: str,
        retry_days: int = 3,
    ):
        if not settings.ENABLE_BILLING_EMAILS:
            return

        recipient_email, recipient_name = await get_billing_email_recipient(db, patient)

        template = self.env.get_template("emails/billing/payment-failed.html")

        # Provide user details even if fallback is used
        patient_name = f"{patient.first_name} {patient.last_name}"

        html_content = template.render(
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            actual_patient_name=patient_name,
            is_proxy_managed=(patient.billing_manager_id is not None),
            amount_dollars=f"{amount_cents / 100:.2f}",
            failure_reason=failure_reason,
            attempt_count=attempt_count,
            update_payment_url=update_payment_url,
            retry_days=retry_days,
            company_name=settings.COMPANY_NAME,
            patient_email=recipient_email,  # needed for footer
        )

        await self.send_email(
            to_email=recipient_email, subject="Payment Failed - Action Required", html_content=html_content
        )

    async def send_subscription_cancelled_email(
        self,
        to_email: str,
        patient_name: str,
        cancellation_type: str,
        cancels_at_period_end: bool,
        period_end_date: datetime | None,
        reactivate_url: str,
    ):
        if not settings.ENABLE_BILLING_EMAILS:
            return

        template = self.env.get_template("emails/billing/subscription-cancelled.html")

        html_content = template.render(
            patient_name=patient_name,
            patient_email=to_email,
            cancellation_type=cancellation_type,
            cancels_at_period_end=cancels_at_period_end,
            period_end_date=period_end_date.strftime("%B %d, %Y") if period_end_date else None,
            reactivate_url=reactivate_url,
            company_name=settings.COMPANY_NAME,
        )

        await self.send_email(to_email=to_email, subject="Subscription Cancelled", html_content=html_content)


email_service = EmailService()
