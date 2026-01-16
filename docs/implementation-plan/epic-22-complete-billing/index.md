# Epic 22: Complete Billing & Subscription Management
**User Story:** As a Patient, Proxy, or Admin, I want comprehensive billing management with automated monthly subscriptions, email confirmations, receipts, and admin controls, so that billing is transparent and manageable.

**Goal:** Complete the Stripe billing integration with patient-facing signup flows, proxy billing management capabilities, email notifications, printable receipts, and full admin controls for managing subscriptions, refunds, and payment history.

## Proxy Billing Management
**Key Requirement:** Patient proxies can sign up for and manage billing on behalf of patients.

- **Subscription Ownership:** Subscriptions remain 1-1 with patients (subscription linked to patient, not proxy)
- **Billing Manager:** Proxies are designated as "billing managers" for specific patients
- **Multi-Patient Management:** A single proxy can manage billing for multiple patients
- **Email Routing:** When a proxy is the billing manager, all billing emails (confirmations, receipts, failures) go to the proxy instead of the patient
- **Formal Data Model:** `billing_manager_id` field on Patient model stores the proxy user ID

## Traceability Matrix
| Plan Step | Story File | Status |
| :--- | :--- | :--- |
| Patient Billing | `story-22-01-patient-billing-api.md` | ✅ Complete |
| Email & Receipts | `story-22-02-email-receipts.md` | ✅ Complete |
| Patient Frontend | `story-22-03-patient-billing-ui.md` | ✅ Complete |
| Admin Billing API | `story-22-04-admin-billing-api.md` | ✅ Complete |
| Admin Frontend | `story-22-05-admin-billing-ui.md` | ✅ Complete |
| Logging & Monitoring | `story-22-06-logging-monitoring.md` | ✅ Complete |
| Testing & Docs | `story-22-07-testing-docs.md` | ✅ Complete |

## Execution Order
1.  [x] `story-22-01-patient-billing-api.md`
2.  [x] `story-22-02-email-receipts.md`
3.  [x] `story-22-03-patient-billing-ui.md`
4.  [x] `story-22-04-admin-billing-api.md`
5.  [x] `story-22-05-admin-billing-ui.md`
6.  [x] `story-22-06-logging-monitoring.md`
7.  [x] `story-22-07-testing-docs.md`

## Epic Verification
**Completion Criteria:**
- [ ] Patients can sign up for monthly subscriptions independently.
- [ ] Proxies can sign up for subscriptions on behalf of patients.
- [ ] Proxies can manage billing for multiple patients from single dashboard.
- [ ] Email confirmations sent to billing manager (proxy or patient).
- [ ] Printable PDF receipts generated and accessible.
- [ ] Patients/proxies can view complete billing history.
- [ ] Patients/proxies can cancel subscriptions from UI.
- [ ] Admins can view all user subscriptions with filters.
- [ ] Admins can assign/remove billing managers.
- [ ] Admins can issue refunds through UI.
- [ ] Admins can grant free subscriptions to users.
- [ ] All payment statements viewable by admins.
- [ ] Comprehensive audit logging for all billing actions.
- [ ] Full test coverage (unit, integration, e2e).
- [ ] Documentation updated for all new endpoints.

## Current State Analysis
**Existing (Epic 15):**
- ✅ Organization-level Stripe integration
- ✅ Basic checkout session creation
- ✅ Webhook handlers (5 events)
- ✅ Billing portal integration
- ✅ Frontend billing page for org admins
- ✅ Database schema supports patient billing

**Gaps to Address:**
- ❌ No patient-facing billing flows
- ❌ No proxy billing management capabilities
- ❌ No billing manager assignment/tracking
- ❌ No email notifications for billing events
- ❌ No receipt/invoice generation
- ❌ No admin dashboard for managing all subscriptions
- ❌ No refund capabilities
- ❌ No free subscription grants
- ❌ Limited payment history visibility
- ❌ Insufficient audit logging
- ❌ Incomplete test coverage for billing flows

## Key Features to Implement

### Patient-Facing Features
1. **Self-Service Subscription Signup**
   - Browse available plans
   - Enter payment information
   - Complete checkout process
   - Receive email confirmation

2. **Billing History**
   - View all past payments
   - Download PDF receipts
   - See upcoming charges
   - View subscription details

3. **Subscription Management**
   - Cancel subscription
   - Update payment method (via Stripe portal)
   - View cancellation status

### Proxy Billing Features
1. **Multi-Patient Billing Dashboard**
   - View all managed patient subscriptions in one place
   - See billing status for each patient
   - Access controls: only manage assigned patients

2. **Subscription Management for Patients**
   - Sign up for subscriptions on behalf of patients
   - Cancel/modify subscriptions for managed patients
   - View transaction history for all managed patients
   - Update payment methods

3. **Email Notifications**
   - Receive all billing emails for managed patients
   - Payment confirmations, receipts, failure alerts
   - Proxy email used instead of patient email

4. **Billing Manager Assignment**
   - Patient or admin can assign proxy as billing manager
   - Proxy accepts billing manager responsibility
   - Assignment tracked in database

### Admin/Staff Features
1. **Subscription Dashboard**
   - View all active subscriptions
   - Filter by status, plan, date range
   - Search by patient name/email
   - View billing manager assignments
   - Export subscription data

2. **Subscription Management**
   - Refund payments
   - Grant free subscriptions
   - Override subscription status
   - Manually cancel subscriptions

3. **Billing Manager Management**
   - Assign/remove billing managers for patients
   - View all proxy-patient billing relationships
   - Audit billing manager access
   - Override billing manager assignments

4. **Payment Analytics**
   - Revenue reports
   - Failed payment tracking
   - Churn analysis
   - MRR (Monthly Recurring Revenue) tracking
   - Billing manager effectiveness metrics

### System Features
1. **Email Notifications**
   - Payment success confirmation
   - Payment failure alerts
   - Subscription cancellation confirmation
   - Upcoming renewal reminders

2. **Receipt Generation**
   - PDF receipts for all payments
   - Printable format
   - Include all transaction details
   - Accessible via email and portal

3. **Audit Logging**
   - Log all billing API calls
   - Track admin actions (refunds, grants)
   - Record subscription changes
   - Monitor webhook events

4. **Testing**
   - Unit tests for all services
   - Integration tests with Stripe test mode
   - E2E tests for complete flows
   - Webhook event testing

## Security & Compliance Considerations
- **PCI Compliance:** Never store raw card data (handled by Stripe)
- **Access Control:**
  - Patient can only view own billing
  - Proxy can only view billing for assigned patients (where they are billing_manager)
  - Admins can view all billing
  - Proxy must have active proxy relationship with patient to manage billing
- **Audit Trail:** All billing actions logged with actor and timestamp
- **Proxy Actions:** All proxy billing actions logged with proxy user ID and patient ID
- **HIPAA:** Billing data not linked to PHI in audit logs
- **Idempotency:** Prevent duplicate charges/refunds
- **Rate Limiting:** Protect billing endpoints from abuse
- **Billing Manager Authorization:** Validate proxy has active access to patient before allowing billing operations

## Technical Architecture

### Updated Patient Model
```sql
-- Add to existing patients table
ALTER TABLE patients ADD COLUMN billing_manager_id UUID REFERENCES users(id);
ALTER TABLE patients ADD COLUMN billing_manager_assigned_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE patients ADD COLUMN billing_manager_assigned_by UUID REFERENCES users(id);

CREATE INDEX idx_patients_billing_manager ON patients(billing_manager_id) WHERE billing_manager_id IS NOT NULL;
```

**Field Definitions:**
- `billing_manager_id`: User ID of the proxy managing billing for this patient (NULL if patient manages own billing)
- `billing_manager_assigned_at`: Timestamp when billing manager was assigned
- `billing_manager_assigned_by`: User ID who assigned the billing manager (patient, admin, or proxy themselves)

### New Database Tables
```sql
billing_transactions (
  id UUID PK,
  owner_id UUID,  -- patient_id or organization_id
  owner_type VARCHAR,  -- 'PATIENT' or 'ORGANIZATION'
  stripe_payment_intent_id VARCHAR UNIQUE,
  stripe_invoice_id VARCHAR,
  amount_cents INTEGER,
  currency VARCHAR(3),
  status VARCHAR,  -- 'SUCCEEDED', 'FAILED', 'REFUNDED', 'PENDING'
  description TEXT,
  receipt_url VARCHAR,
  created_at TIMESTAMP,
  refunded_at TIMESTAMP,
  refunded_by UUID,
  refund_reason TEXT,
  managed_by_proxy_id UUID  -- Proxy user ID if transaction was initiated by proxy
)

subscription_overrides (
  id UUID PK,
  owner_id UUID,
  owner_type VARCHAR,
  override_type VARCHAR,  -- 'FREE', 'TRIAL_EXTENSION', 'MANUAL_CANCEL'
  granted_by UUID,
  reason TEXT,
  expires_at TIMESTAMP,
  created_at TIMESTAMP
)
```

### New API Endpoints

**Patient Billing:**
- `POST /api/v1/patients/{patient_id}/billing/checkout`
- `GET /api/v1/patients/{patient_id}/billing/subscription`
- `POST /api/v1/patients/{patient_id}/billing/portal`
- `GET /api/v1/patients/{patient_id}/billing/transactions`
- `GET /api/v1/patients/{patient_id}/billing/receipts/{receipt_id}`
- `POST /api/v1/patients/{patient_id}/billing/cancel`
- `PUT /api/v1/patients/{patient_id}/billing/manager` - Assign billing manager
- `DELETE /api/v1/patients/{patient_id}/billing/manager` - Remove billing manager

**Proxy Billing:**
- `GET /api/v1/proxy/managed-patients/billing` - List all managed patient subscriptions
- `GET /api/v1/proxy/managed-patients/{patient_id}/billing/subscription` - Get specific patient subscription
- `POST /api/v1/proxy/managed-patients/{patient_id}/billing/checkout` - Create checkout for patient
- `POST /api/v1/proxy/managed-patients/{patient_id}/billing/cancel` - Cancel patient subscription
- `GET /api/v1/proxy/managed-patients/{patient_id}/billing/transactions` - View patient transactions

**Admin Billing:**
- `GET /api/v1/admin/billing/subscriptions`
- `POST /api/v1/admin/billing/subscriptions/{subscription_id}/refund`
- `POST /api/v1/admin/billing/subscriptions/{subscription_id}/grant-free`
- `GET /api/v1/admin/billing/transactions`
- `GET /api/v1/admin/billing/analytics`
- `POST /api/v1/admin/billing/subscriptions/{subscription_id}/cancel`
- `PUT /api/v1/admin/patients/{patient_id}/billing/manager` - Assign billing manager (admin)
- `GET /api/v1/admin/billing/managers` - List all billing manager relationships

### Email Templates
- `billing/payment-success.html`
- `billing/payment-failed.html`
- `billing/subscription-cancelled.html`
- `billing/upcoming-renewal.html`
- `billing/receipt-pdf.html` (for PDF generation)

## Dependencies
- **Existing:**
  - Epic 15 (Billing) must be complete
  - Epic 14 (Proxies) must be complete - proxy relationship model required
- **Required Services:**
  - Stripe SDK (already integrated)
  - Email service (from Epic 16: Notifications)
  - PDF generation library (e.g., WeasyPrint, ReportLab)
  - Proxy access validation service
- **Environment Variables:**
  - All existing Stripe config
  - `BILLING_EMAIL_FROM` - sender email for billing notifications
  - `ENABLE_BILLING_EMAILS` - feature flag for email notifications
  - `ENABLE_PROXY_BILLING` - feature flag for proxy billing management

## Rollout Plan
1. Deploy backend APIs (Stories 22.1, 22.4)
2. Enable webhook logging (Story 22.6)
3. Deploy email notifications (Story 22.2)
4. Deploy patient UI (Story 22.3)
5. Deploy admin UI (Story 22.5)
6. Monitor for 1 week in production
7. Gradually enable for all users

## Success Metrics
- **Patient Adoption:** % of patients who sign up for billing
- **Self-Service Rate:** % of billing actions done without staff intervention
- **Payment Success Rate:** % of payments that succeed on first attempt
- **Admin Efficiency:** Time saved managing subscriptions
- **Support Tickets:** Reduction in billing-related support requests
