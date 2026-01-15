# Billing System Documentation

Complete Stripe-integrated billing system supporting both organization and patient-level subscriptions with proxy billing management.

## Overview

The billing system provides:

- **Patient Self-Service**: Subscribers can sign up for monthly subscriptions independently
- **Proxy Billing Management**: Proxies can manage billing on behalf of patients
- **Admin Dashboard**: Full admin controls for subscriptions, refunds, and analytics
- **Email Notifications**: Automated payment confirmations and receipts
- **Comprehensive Audit Logging**: All billing actions logged for HIPAA compliance

## Architecture

### API Endpoints

#### Patient Billing (`/api/v1/patients/{patient_id}/billing/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/checkout` | POST | Create checkout session for subscription |
| `/subscription` | GET | Get subscription status |
| `/portal` | POST | Create Stripe billing portal session |
| `/transactions` | GET | List payment transactions |
| `/cancel` | POST | Cancel subscription |
| `/manager` | PUT | Assign billing manager |
| `/manager` | DELETE | Remove billing manager |

#### Proxy Billing (`/api/v1/proxy/managed-patients/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/billing` | GET | List all managed patient subscriptions |
| `/{patient_id}/billing/subscription` | GET | Get patient subscription |
| `/{patient_id}/billing/checkout` | POST | Create checkout for patient |
| `/{patient_id}/billing/cancel` | POST | Cancel patient subscription |

#### Admin Billing (`/api/v1/admin/billing/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/subscriptions` | GET | List all subscriptions with filters |
| `/transactions` | GET | List all transactions |
| `/transactions/{id}/refund` | POST | Issue refund |
| `/grant-free` | POST | Grant free subscription |
| `/subscriptions/{type}/{id}/cancel` | POST | Admin cancel subscription |
| `/analytics` | GET | Get billing analytics |
| `/managers` | GET | List billing manager relationships |

## Database Models

### billing_transactions

Stores all payment transactions:

```sql
billing_transactions (
  id UUID PK,
  owner_id UUID,
  owner_type VARCHAR -- 'PATIENT' or 'ORGANIZATION'
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
  managed_by_proxy_id UUID
)
```

### subscription_overrides

Tracks free subscriptions and other overrides:

```sql
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

### Patient Billing Manager Fields

```sql
-- On patients table
billing_manager_id UUID REFERENCES users(id)
billing_manager_assigned_at TIMESTAMP
billing_manager_assigned_by UUID REFERENCES users(id)
```

## Billing Manager System

Proxies can be designated as billing managers for patients:

1. **Assignment**: Patient, admin, or proxy can assign billing manager
2. **Email Routing**: All billing emails go to billing manager instead of patient
3. **Authorization**: Billing manager must have active proxy relationship
4. **Multi-Patient**: One proxy can manage billing for multiple patients

## Frontend Components

### Admin Dashboard (`/admin/billing-management`)

- **Analytics Cards**: Total MRR, Active Subscriptions, Churn Rate, ARPU, Failed Payments
- **Subscriptions Tab**: Searchable table with filters, actions (grant free, cancel)
- **Transactions Tab**: Payment history with refund capability
- **Billing Managers Tab**: All proxy-patient billing relationships

### Patient Billing (`/patient/billing`)

- View subscription status
- Access Stripe billing portal
- View transaction history
- Assign/remove billing manager

## Stripe Integration

### Webhook Events

Handled events:
- `checkout.session.completed`
- `invoice.payment_succeeded`
- `invoice.payment_failed`
- `customer.subscription.updated`
- `customer.subscription.deleted`

### Security

- Webhook signature verification
- PCI compliance (no raw card data stored)
- All operations logged to audit trail

## Monitoring & Alerting

### Audit Logging

All billing events logged via `BillingAuditService`:
- Checkout creation
- Payment success/failure
- Refunds
- Subscription changes
- Billing manager assignments

### Metrics

Tracked via `BillingMetricsService`:
- `billing_checkouts_created_total`
- `billing_payments_succeeded_total`
- `billing_payments_failed_total`
- `billing_refunds_issued_total`
- `billing_subscriptions_cancelled_total`

### Alerts

Automated alerts via `BillingAlertsService`:
- Payment failure after 3 attempts
- Webhook processing failures
- High churn rate (>5%)
- Unusual refund activity

## Testing

```bash
# Run all billing tests
docker compose exec api python -m pytest tests/api/test_admin_billing.py tests/api/test_patients_billing.py tests/api/test_proxy_billing.py tests/services/test_billing_audit.py -v

# Run specific test file
docker compose exec api python -m pytest tests/api/test_admin_billing.py -v
```

## Configuration

Required environment variables:

```env
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_SUCCESS_URL=http://localhost:5173/billing/success
STRIPE_CANCEL_URL=http://localhost:5173/billing/cancel
ENABLE_BILLING_EMAILS=true
BILLING_EMAIL_FROM=billing@example.com
BILLING_ALERT_EMAILS=admin@example.com
ENABLE_BILLING_ALERTS=true
```
