# Story 22.2: Email Notifications & Receipt Generation
**User Story:** As a Patient or Proxy (Billing Manager), I want to receive email confirmations and printable receipts for all billing events, so that I have records of payments.

## Status
- [x] **Complete** (core implementation done; minor UI polish remaining)

## Context
- **Epic:** Epic 22 - Complete Billing & Subscription Management
- **Dependencies:**
  - Story 22.1 (Patient Billing API) - includes billing_manager_id field
  - Epic 16 (Notifications & Messaging) - email service
- **Existing Code:**
  - `backend/src/services/email.py` - Email service
  - `backend/templates/` - Email templates directory

## Proxy Email Routing Requirements
**Key Feature:** Billing emails sent to proxy when they are designated billing manager.

- Check `patient.billing_manager_id` to determine email recipient
- If billing_manager_id is set, send emails to proxy's email address
- If billing_manager_id is NULL, send emails to patient's email address
- Email templates indicate when proxy is managing billing (context for proxy)
- Include both proxy name and patient name in email for clarity

## Technical Specification
**Goal:** Implement automated email notifications for all billing events and generate PDF receipts.

### Changes Required

#### 1. Install PDF Generation Library
```bash
# Add to backend/pyproject.toml
[project.dependencies]
weasyprint = "^62.0"  # For HTML to PDF conversion
jinja2 = "^3.1.0"  # Template engine (may already exist)
```

#### 2. Email Templates: `backend/templates/emails/billing/`

**`payment-success.html`:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #4F46E5; color: white; padding: 20px; text-align: center; }
        .content { background: #f9fafb; padding: 30px; }
        .receipt-box { background: white; border: 1px solid #e5e7eb; padding: 20px; margin: 20px 0; }
        .amount { font-size: 32px; font-weight: bold; color: #4F46E5; }
        .details { margin: 20px 0; }
        .details-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb; }
        .button { background: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; display: inline-block; margin: 20px 0; border-radius: 6px; }
        .footer { text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Payment Successful</h1>
        </div>
        <div class="content">
            <p>Hi {{ recipient_name }},</p>

            {% if is_proxy_managed %}
            <p style="background: #EEF2FF; padding: 15px; border-radius: 6px; margin: 20px 0;">
                This is a billing notification for <strong>{{ actual_patient_name }}</strong>'s subscription,
                which you manage as their billing manager.
            </p>
            {% endif %}

            <p>Thank you for your payment. {% if is_proxy_managed %}The{% else %}Your{% endif %} subscription is now active.</p>

            <div class="receipt-box">
                <div class="amount">${{ amount_dollars }}</div>
                <p style="color: #6b7280; margin: 5px 0;">Payment received</p>

                <div class="details">
                    <div class="details-row">
                        <span>Receipt Number</span>
                        <strong>{{ receipt_number }}</strong>
                    </div>
                    <div class="details-row">
                        <span>Date</span>
                        <strong>{{ payment_date }}</strong>
                    </div>
                    <div class="details-row">
                        <span>Payment Method</span>
                        <strong>{{ payment_method }}</strong>
                    </div>
                    <div class="details-row">
                        <span>Subscription Plan</span>
                        <strong>{{ plan_name }}</strong>
                    </div>
                    <div class="details-row">
                        <span>Billing Period</span>
                        <strong>{{ billing_period }}</strong>
                    </div>
                </div>
            </div>

            <p>A PDF receipt is attached to this email for your records.</p>

            <a href="{{ receipt_url }}" class="button">View Receipt Online</a>

            <p>If you have any questions about your subscription, please contact our support team.</p>
        </div>
        <div class="footer">
            <p>{{ company_name }}<br>
            This email was sent to {{ patient_email }}</p>
        </div>
    </div>
</body>
</html>
```

**`payment-failed.html`:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        /* Similar styling as above */
        .header { background: #DC2626; color: white; }
        .alert { background: #FEF2F2; border-left: 4px solid #DC2626; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Payment Failed</h1>
        </div>
        <div class="content">
            <p>Hi {{ recipient_name }},</p>

            {% if is_proxy_managed %}
            <p style="background: #EEF2FF; padding: 15px; border-radius: 6px; margin: 20px 0;">
                This is a billing notification for <strong>{{ actual_patient_name }}</strong>'s subscription.
            </p>
            {% endif %}

            <div class="alert">
                <strong>Action Required:</strong> {% if is_proxy_managed %}A{% else %}Your{% endif %} recent payment of ${{ amount_dollars }} could not be processed.
            </div>

            <p><strong>Reason:</strong> {{ failure_reason }}</p>
            <p><strong>Attempt:</strong> {{ attempt_count }} of 3</p>

            <p>To avoid service interruption, please update your payment method:</p>

            <a href="{{ update_payment_url }}" class="button">Update Payment Method</a>

            <p>We will automatically retry the payment in {{ retry_days }} days. If all attempts fail, your subscription will be cancelled.</p>

            <p>If you believe this is an error or need assistance, please contact our support team immediately.</p>
        </div>
        <div class="footer">
            <p>{{ company_name }}<br>
            This email was sent to {{ patient_email }}</p>
        </div>
    </div>
</body>
</html>
```

**`subscription-cancelled.html`:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        /* Similar styling */
        .header { background: #F59E0B; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Subscription Cancelled</h1>
        </div>
        <div class="content">
            <p>Hi {{ patient_name }},</p>

            <p>Your subscription has been {{ cancellation_type }}.</p>

            {% if cancels_at_period_end %}
            <p>You will retain access to your subscription until <strong>{{ period_end_date }}</strong>. After this date, your subscription will end and you will no longer be charged.</p>
            {% else %}
            <p>Your subscription has been cancelled immediately and you will not be charged again.</p>
            {% endif %}

            <p>If you cancelled by mistake or would like to reactivate your subscription, you can do so at any time:</p>

            <a href="{{ reactivate_url }}" class="button">Reactivate Subscription</a>

            <p>We're sorry to see you go. If you have feedback about your experience, we'd love to hear from you.</p>
        </div>
        <div class="footer">
            <p>{{ company_name }}<br>
            This email was sent to {{ patient_email }}</p>
        </div>
    </div>
</body>
</html>
```

**`upcoming-renewal.html`:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        /* Similar styling */
        .header { background: #0891B2; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Upcoming Renewal</h1>
        </div>
        <div class="content">
            <p>Hi {{ patient_name }},</p>

            <p>This is a friendly reminder that your subscription will automatically renew on <strong>{{ renewal_date }}</strong>.</p>

            <div class="receipt-box">
                <div class="details">
                    <div class="details-row">
                        <span>Plan</span>
                        <strong>{{ plan_name }}</strong>
                    </div>
                    <div class="details-row">
                        <span>Amount</span>
                        <strong>${{ amount_dollars }}</strong>
                    </div>
                    <div class="details-row">
                        <span>Renewal Date</span>
                        <strong>{{ renewal_date }}</strong>
                    </div>
                    <div class="details-row">
                        <span>Payment Method</span>
                        <strong>{{ payment_method }}</strong>
                    </div>
                </div>
            </div>

            <p>No action is required. Your payment method will be charged automatically.</p>

            <a href="{{ manage_subscription_url }}" class="button">Manage Subscription</a>

            <p>To update your payment method or cancel your subscription, please visit your billing portal.</p>
        </div>
        <div class="footer">
            <p>{{ company_name }}<br>
            This email was sent to {{ patient_email }}</p>
        </div>
    </div>
</body>
</html>
```

#### 3. PDF Receipt Template: `backend/templates/receipts/receipt-pdf.html`
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @page { size: A4; margin: 1cm; }
        body { font-family: Arial, sans-serif; font-size: 12pt; }
        .receipt { max-width: 21cm; margin: 0 auto; }
        .header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 20px; margin-bottom: 30px; }
        .logo { font-size: 24pt; font-weight: bold; color: #4F46E5; }
        .receipt-title { font-size: 18pt; margin: 10px 0; }
        .info-section { margin: 20px 0; }
        .info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e5e7eb; }
        .total { font-size: 20pt; font-weight: bold; text-align: right; margin-top: 30px; padding: 15px; background: #f3f4f6; }
        .footer { text-align: center; margin-top: 50px; font-size: 10pt; color: #6b7280; }
    </style>
</head>
<body>
    <div class="receipt">
        <div class="header">
            <div class="logo">{{ company_name }}</div>
            <div>{{ company_address }}</div>
            <div>{{ company_phone }} | {{ company_email }}</div>
            <h2 class="receipt-title">PAYMENT RECEIPT</h2>
        </div>

        <div class="info-section">
            <div class="info-row">
                <span><strong>Receipt Number:</strong></span>
                <span>{{ receipt_number }}</span>
            </div>
            <div class="info-row">
                <span><strong>Date:</strong></span>
                <span>{{ payment_date }}</span>
            </div>
            <div class="info-row">
                <span><strong>Customer:</strong></span>
                <span>{{ patient_name }}</span>
            </div>
            <div class="info-row">
                <span><strong>Email:</strong></span>
                <span>{{ patient_email }}</span>
            </div>
        </div>

        <div class="info-section">
            <h3>Payment Details</h3>
            <div class="info-row">
                <span>Subscription Plan - {{ plan_name }}</span>
                <span>${{ amount_dollars }}</span>
            </div>
            <div class="info-row">
                <span>Billing Period</span>
                <span>{{ billing_period }}</span>
            </div>
            <div class="info-row">
                <span>Payment Method</span>
                <span>{{ payment_method }}</span>
            </div>
            <div class="info-row">
                <span>Transaction ID</span>
                <span>{{ transaction_id }}</span>
            </div>
        </div>

        <div class="total">
            Total Paid: ${{ amount_dollars }} {{ currency }}
        </div>

        <div class="footer">
            <p>Thank you for your payment!</p>
            <p>This is a computer-generated receipt and does not require a signature.</p>
            <p>For questions, contact {{ support_email }}</p>
        </div>
    </div>
</body>
</html>
```

#### 4. Service: `backend/src/services/receipt.py` (NEW)
```python
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import io
from datetime import datetime

class ReceiptGenerator:
    def __init__(self):
        template_dir = Path(__file__).parent.parent / "templates" / "receipts"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

    def generate_pdf_receipt(
        self,
        transaction: BillingTransaction,
        patient: Patient,
        plan_name: str,
        billing_period: str,
        payment_method: str
    ) -> bytes:
        """Generate PDF receipt from transaction"""
        template = self.env.get_template("receipt-pdf.html")

        html_content = template.render(
            company_name=settings.COMPANY_NAME,
            company_address=settings.COMPANY_ADDRESS,
            company_phone=settings.COMPANY_PHONE,
            company_email=settings.COMPANY_EMAIL,
            support_email=settings.SUPPORT_EMAIL,
            receipt_number=transaction.receipt_number,
            payment_date=transaction.created_at.strftime("%B %d, %Y"),
            patient_name=f"{patient.first_name} {patient.last_name}",
            patient_email=patient.email,
            plan_name=plan_name,
            amount_dollars=f"{transaction.amount_cents / 100:.2f}",
            currency=transaction.currency.upper(),
            billing_period=billing_period,
            payment_method=payment_method,
            transaction_id=transaction.stripe_payment_intent_id or transaction.id
        )

        # Generate PDF
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes

    async def save_receipt_to_storage(
        self,
        pdf_bytes: bytes,
        transaction_id: str
    ) -> str:
        """Save PDF to storage and return URL"""
        # If using S3 or similar:
        filename = f"receipts/{transaction_id}.pdf"
        # Upload to S3 and return URL
        # For now, save locally:
        receipt_path = Path(settings.RECEIPTS_DIR) / f"{transaction_id}.pdf"
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_bytes(pdf_bytes)
        return f"/api/v1/receipts/{transaction_id}.pdf"

receipt_generator = ReceiptGenerator()
```

#### 5. Email Service Extension: `backend/src/services/email.py` (EXTEND)
```python
# Add billing-specific email methods

async def send_payment_success_email(
    db: AsyncSession,  # NEW: Add db to get billing manager
    patient: Patient,  # NEW: Pass full patient object instead of just email/name
    amount_cents: int,
    receipt_number: str,
    payment_date: datetime,
    payment_method: str,
    plan_name: str,
    billing_period: str,
    receipt_url: str,
    pdf_attachment: bytes
):
    """Send payment success confirmation with receipt"""
    # NEW: Get email recipient (patient or billing manager)
    from ..services.billing_access import get_billing_email_recipient
    recipient_email, recipient_name = await get_billing_email_recipient(db, patient)

    template = env.get_template("emails/billing/payment-success.html")

    html_content = template.render(
        recipient_name=recipient_name,  # NEW: Recipient (proxy or patient)
        recipient_email=recipient_email,
        actual_patient_name=f"{patient.first_name} {patient.last_name}",  # NEW: Actual patient
        is_proxy_managed=patient.billing_manager_id is not None,  # NEW: Flag
        amount_dollars=f"{amount_cents / 100:.2f}",
        receipt_number=receipt_number,
        payment_date=payment_date.strftime("%B %d, %Y"),
        payment_method=payment_method,
        plan_name=plan_name,
        billing_period=billing_period,
        receipt_url=receipt_url,
        company_name=settings.COMPANY_NAME
    )

    await send_email(
        to_email=recipient_email,  # NEW: Send to proxy if assigned
        subject=f"Payment Successful - Receipt {receipt_number}",
        html_content=html_content,
        attachments=[{
            "filename": f"receipt-{receipt_number}.pdf",
            "content": pdf_attachment,
            "content_type": "application/pdf"
        }]
    )

async def send_payment_failed_email(
    db: AsyncSession,  # NEW: Add db parameter
    patient: Patient,  # NEW: Pass patient object
    amount_cents: int,
    failure_reason: str,
    attempt_count: int,
    update_payment_url: str,
    retry_days: int = 3
):
    """Send payment failure notification"""
    # NEW: Get email recipient
    from ..services.billing_access import get_billing_email_recipient
    recipient_email, recipient_name = await get_billing_email_recipient(db, patient)

    template = env.get_template("emails/billing/payment-failed.html")

    html_content = template.render(
        recipient_name=recipient_name,  # NEW
        recipient_email=recipient_email,  # NEW
        actual_patient_name=f"{patient.first_name} {patient.last_name}",  # NEW
        is_proxy_managed=patient.billing_manager_id is not None,  # NEW
        amount_dollars=f"{amount_cents / 100:.2f}",
        failure_reason=failure_reason,
        attempt_count=attempt_count,
        update_payment_url=update_payment_url,
        retry_days=retry_days,
        company_name=settings.COMPANY_NAME
    )

    await send_email(
        to_email=to_email,
        subject="Payment Failed - Action Required",
        html_content=html_content
    )

async def send_subscription_cancelled_email(
    to_email: str,
    patient_name: str,
    cancellation_type: str,
    cancels_at_period_end: bool,
    period_end_date: datetime | None,
    reactivate_url: str
):
    """Send subscription cancellation confirmation"""
    template = env.get_template("emails/billing/subscription-cancelled.html")

    html_content = template.render(
        patient_name=patient_name,
        patient_email=to_email,
        cancellation_type=cancellation_type,
        cancels_at_period_end=cancels_at_period_end,
        period_end_date=period_end_date.strftime("%B %d, %Y") if period_end_date else None,
        reactivate_url=reactivate_url,
        company_name=settings.COMPANY_NAME
    )

    await send_email(
        to_email=to_email,
        subject="Subscription Cancelled",
        html_content=html_content
    )

async def send_upcoming_renewal_email(
    to_email: str,
    patient_name: str,
    plan_name: str,
    amount_cents: int,
    renewal_date: datetime,
    payment_method: str,
    manage_subscription_url: str
):
    """Send upcoming renewal reminder (3 days before)"""
    template = env.get_template("emails/billing/upcoming-renewal.html")

    html_content = template.render(
        patient_name=patient_name,
        patient_email=to_email,
        plan_name=plan_name,
        amount_dollars=f"{amount_cents / 100:.2f}",
        renewal_date=renewal_date.strftime("%B %d, %Y"),
        payment_method=payment_method,
        manage_subscription_url=manage_subscription_url,
        company_name=settings.COMPANY_NAME
    )

    await send_email(
        to_email=to_email,
        subject="Your Subscription Renews Soon",
        html_content=html_content
    )
```

#### 6. Webhook Integration: `backend/src/api/webhooks.py` (EXTEND)
```python
# Add email triggers to webhook handlers

async def _handle_payment_succeeded(event: dict, db: AsyncSession) -> WebhookResult:
    """Handle successful payment - send email with receipt"""
    invoice = event["data"]["object"]
    customer_id = invoice["customer"]

    # Existing transaction recording...
    transaction = await record_transaction(...)

    # NEW: Generate and send receipt
    owner_id, owner_type = await _get_owner_from_customer(customer_id, db)

    if owner_type == "PATIENT":
        patient = await db.get(Patient, owner_id)

        # Generate PDF receipt
        pdf_bytes = receipt_generator.generate_pdf_receipt(
            transaction=transaction,
            patient=patient,
            plan_name=invoice["lines"]["data"][0]["description"],
            billing_period=f"{invoice['period_start']} - {invoice['period_end']}",
            payment_method=f"Card ending in {invoice['payment_method']['card']['last4']}"
        )

        # Save receipt
        receipt_url = await receipt_generator.save_receipt_to_storage(
            pdf_bytes, str(transaction.id)
        )

        # Send email (NEW: Pass db and patient object)
        await email_service.send_payment_success_email(
            db=db,  # NEW
            patient=patient,  # NEW: Full patient object
            amount_cents=transaction.amount_cents,
            receipt_number=transaction.receipt_number,
            payment_date=transaction.created_at,
            payment_method=f"Card ending in {invoice['payment_method']['card']['last4']}",
            plan_name=invoice["lines"]["data"][0]["description"],
            billing_period=f"{invoice['period_start']} - {invoice['period_end']}",
            receipt_url=receipt_url,
            pdf_attachment=pdf_bytes
        )
        # Email will automatically be sent to billing manager if assigned

    return WebhookResult(...)

async def _handle_payment_failed(event: dict, db: AsyncSession) -> WebhookResult:
    """Handle failed payment - send alert email"""
    invoice = event["data"]["object"]
    customer_id = invoice["customer"]

    # Existing status update...

    # NEW: Send failure email (automatically routed to billing manager if assigned)
    owner_id, owner_type = await _get_owner_from_customer(customer_id, db)

    if owner_type == "PATIENT":
        patient = await db.get(Patient, owner_id)

        await email_service.send_payment_failed_email(
            to_email=patient.email,
            patient_name=f"{patient.first_name} {patient.last_name}",
            amount_cents=invoice["amount_due"],
            failure_reason=invoice.get("last_finalization_error", {}).get("message", "Unknown"),
            attempt_count=invoice["attempt_count"],
            update_payment_url=f"{settings.FRONTEND_URL}/patient/billing"
        )

    return WebhookResult(...)
```

#### 7. Scheduled Task: `backend/src/tasks/billing_reminders.py` (NEW)
```python
from celery import Celery
from datetime import datetime, timedelta
from sqlalchemy import select

# Celery task to send renewal reminders 3 days before renewal

@celery.task
async def send_renewal_reminders():
    """Send renewal reminders for subscriptions renewing in 3 days"""
    target_date = datetime.utcnow() + timedelta(days=3)

    # Query Stripe for upcoming renewals
    # Send emails to patients with upcoming renewals

    # (Implementation depends on your Celery setup)
    pass
```

#### 8. Configuration: `backend/src/config.py` (EXTEND)
```python
# Add billing email settings
ENABLE_BILLING_EMAILS: bool = Field(default=True)
BILLING_EMAIL_FROM: str = Field(default="billing@example.com")
RECEIPTS_DIR: str = Field(default="./storage/receipts")
COMPANY_NAME: str = Field(default="Your Company")
COMPANY_ADDRESS: str = Field(default="123 Main St, City, State 12345")
COMPANY_PHONE: str = Field(default="(555) 123-4567")
COMPANY_EMAIL: str = Field(default="info@example.com")
SUPPORT_EMAIL: str = Field(default="support@example.com")
```

## Acceptance Criteria
- [x] WeasyPrint installed and PDF generation works.
- [x] All 4 email templates created (success, failed, cancelled, renewal).
- [x] Email templates include proxy billing manager context.
- [x] PDF receipt template created with proper formatting.
- [x] Email sent on successful payment with PDF attachment.
- [x] Email sent on failed payment with action link.
- [x] Email sent on subscription cancellation.
- [x] PDF receipts generated and stored.
- [x] Receipts accessible via URL in patient transaction history.
- [x] **Proxy Billing:** Emails sent to billing manager when assigned.
- [x] **Proxy Billing:** Emails sent to patient when no billing manager.
- [x] **Proxy Billing:** Email clearly indicates patient name when proxy is recipient.
- [ ] All emails include unsubscribe link (if required by law).
- [ ] Email templates responsive and render correctly in major email clients.

## Verification Plan
**Automated Tests:**
```bash
pytest tests/services/test_receipt_generator.py -v
pytest tests/services/test_billing_emails.py -v
```

**Test Cases:**
1. Generate PDF receipt from transaction
2. Send payment success email with attachment
3. Send payment failed email with correct attempt count
4. Send cancellation confirmation
5. Verify email template rendering
6. Test PDF formatting on different paper sizes
7. **Proxy Billing:** Email sent to proxy when billing_manager_id set
8. **Proxy Billing:** Email sent to patient when billing_manager_id is NULL
9. **Proxy Billing:** Email template shows patient context for proxy
10. **Proxy Billing:** Verify `get_billing_email_recipient()` function works correctly

**Manual Verification:**
1. Trigger test payment webhook
2. Check email inbox for confirmation
3. Verify PDF attachment is valid and printable
4. Test email rendering in Gmail, Outlook, Apple Mail
5. Verify all links in emails work correctly
6. Check receipt stored in correct location

## Security Considerations
- [ ] Never include full payment method details in emails
- [ ] Sanitize all user data before rendering in templates
- [ ] Use secure storage for PDF receipts (S3 with presigned URLs)
- [ ] Implement rate limiting on receipt generation
- [ ] Validate receipt access (only owner can download)
- [ ] Include security notice in emails about phishing

## Performance Considerations
- [ ] Generate PDFs asynchronously (use Celery/background task)
- [ ] Cache rendered email templates
- [ ] Compress PDF files if size > 1MB
- [ ] Use CDN for email assets (logos, images)
- [ ] Batch email sending for multiple recipients

## Rollback Plan
If issues arise:
1. Disable email sending via `ENABLE_BILLING_EMAILS=false`
2. Continue recording transactions without email
3. Manually send receipts if needed
4. Fix email/PDF issues in staging
5. Re-enable after verification
