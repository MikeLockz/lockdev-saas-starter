from datetime import datetime
from pathlib import Path
from uuid import UUID

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from src.config import settings
from src.models.billing import BillingTransaction
from src.models.profiles import Patient


class ReceiptGenerator:
    def __init__(self):
        # Determine the template directory based on backend structure
        # Assuming apps/backend/src/templates/receipts relative to this file?
        # This file is in apps/backend/src/services/receipt.py
        # root is apps/backend/src
        # So templates should be ../templates/receipts

        base_dir = Path(__file__).parent.parent
        self.template_dir = base_dir / "templates" / "receipts"
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))

    def generate_pdf_receipt(
        self,
        transaction: BillingTransaction,
        patient: Patient,
        plan_name: str,
        billing_period: str,
        payment_method: str,
    ) -> bytes:
        """Generate PDF receipt from transaction"""
        template = self.env.get_template("receipt-pdf.html")

        # Format amount
        amount_dollar = f"{transaction.amount_cents / 100:.2f}"

        # Format date
        # Fallback to now if created_at is None (should not happen)
        # created_at is naive or timezone aware? default usually naive in some setups, but using UTC
        payment_date = (
            transaction.created_at.strftime("%B %d, %Y")
            if transaction.created_at
            else datetime.now().strftime("%B %d, %Y")
        )

        html_content = template.render(
            company_name=settings.COMPANY_NAME,
            company_address=settings.COMPANY_ADDRESS,
            company_phone=settings.COMPANY_PHONE,
            company_email=settings.COMPANY_EMAIL,
            support_email=settings.SUPPORT_EMAIL,
            receipt_number=transaction.receipt_number or str(transaction.id),
            payment_date=payment_date,
            patient_name=f"{patient.first_name} {patient.last_name}",
            patient_email=patient.user.email if patient.user else "example@email.com",  # Fallback
            plan_name=plan_name,
            amount_dollars=amount_dollar,
            currency=transaction.currency.upper(),
            billing_period=billing_period,
            payment_method=payment_method,
            transaction_id=transaction.stripe_payment_intent_id or str(transaction.id),
        )

        # Generate PDF
        # write_pdf returns bytes if target is not specified
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes

    async def save_receipt_to_storage(self, pdf_bytes: bytes, transaction_id: str | UUID) -> str:
        """
        Save PDF to storage and return URL.
        Ideally this uploads to S3. For now, saving locally.
        """
        filename = f"{transaction_id}.pdf"

        # Attempt S3 Upload
        if settings.AWS_S3_BUCKET:
            try:
                import boto3

                s3 = boto3.client("s3", region_name=settings.AWS_REGION)
                key = f"receipts/{filename}"

                # Run sync boto3 in threadpool if strictly async, but for now direct call (it's blocking but fast usually)
                # Ideally use aiboto3 or run_in_executor
                import asyncio
                from functools import partial

                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    partial(
                        s3.put_object,
                        Bucket=settings.AWS_S3_BUCKET,
                        Key=key,
                        Body=pdf_bytes,
                        ContentType="application/pdf",
                    ),
                )

                # Generate presigned URL
                url = await loop.run_in_executor(
                    None,
                    partial(
                        s3.generate_presigned_url,
                        "get_object",
                        Params={"Bucket": settings.AWS_S3_BUCKET, "Key": key},
                        ExpiresIn=604800,  # 7 days
                    ),
                )
                return url

            except Exception as e:
                # Log error and fall back to local
                print(f"S3 Upload failed: {e}")

        # Local Fallback
        storage_path = Path(settings.RECEIPTS_DIR)

        # Create directory if not exists
        storage_path.mkdir(parents=True, exist_ok=True)

        file_path = storage_path / filename
        file_path.write_bytes(pdf_bytes)

        # Return valid URL path that can be served
        return f"/api/v1/receipts/{filename}"


receipt_generator = ReceiptGenerator()
