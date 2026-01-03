# Story 15.2: Stripe Webhooks
**User Story:** As the System, I want to handle Stripe events to keep subscription status in sync.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 4.2 from `docs/10 - application implementation plan.md`
- **Existing:** Webhook endpoint exists in `backend/src/api/webhooks.py`

## Technical Specification
**Goal:** Handle Stripe webhook events for subscription lifecycle.

**Changes Required:**

1.  **Update:** `backend/src/api/webhooks.py`
    - `POST /webhooks/stripe`
      - Verify webhook signature
      - Handle events:
        - `checkout.session.completed` → Create subscription record
        - `invoice.paid` → Update subscription status to ACTIVE
        - `invoice.payment_failed` → Update status to PAST_DUE
        - `customer.subscription.updated` → Sync plan changes
        - `customer.subscription.deleted` → Update status to CANCELLED

2.  **Service:** `backend/src/services/billing.py`
    - `handle_checkout_completed(session)`
    - `handle_invoice_paid(invoice)`
    - `handle_subscription_updated(subscription)`
    - `handle_subscription_deleted(subscription)`

3.  **Database Updates:**
    - Update `organizations.subscription_status`
    - Update `organizations.stripe_customer_id` if new

4.  **Error Handling:**
    - Return 200 for handled events
    - Return 400 for invalid signature
    - Log unhandled event types

## Acceptance Criteria
- [ ] Webhook signature verified correctly.
- [ ] `checkout.session.completed` creates subscription.
- [ ] `invoice.paid` updates status to ACTIVE.
- [ ] `invoice.payment_failed` updates status to PAST_DUE.
- [ ] Subscription cancellation handled.
- [ ] Unhandled events logged but return 200.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_webhooks.py::test_stripe_signature`
- `pytest tests/api/test_webhooks.py::test_invoice_paid`

**Manual Verification:**
- Use Stripe CLI: `stripe trigger invoice.paid`
- Verify organization status updated in database.
