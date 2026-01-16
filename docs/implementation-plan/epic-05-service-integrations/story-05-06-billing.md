# Story 5.6: Billing (Stripe)
**User Story:** As a Business Owner, I want to charge customers, so that the business is sustainable.

## Status
- [x] **Complete**

## Context
- **Roadmap Ref:** Step 5.6 from `docs/03`

## Technical Specification
**Goal:** Integrate Stripe Subscriptions.

**Changes Required:**
1.  **File:** `backend/src/services/billing.py`
    - `create_customer`, `create_checkout_session`, `create_portal_session`.
    - Complete webhook event handlers for subscription lifecycle.
2.  **File:** `backend/src/api/webhooks.py`
    - Handle `checkout.session.completed`, `invoice.payment_succeeded`, etc.
    - Verify signature with `stripe.Webhook.construct_event`.
3.  **File:** `backend/src/config.py`
    - Added `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`, success/cancel URLs.

## Acceptance Criteria
- [x] Can create checkout session.
- [x] Webhook updates DB status.

## Verification Plan
**Manual Verification:**
- Use Stripe CLI to forward webhooks to localhost. Trigger test payment.
