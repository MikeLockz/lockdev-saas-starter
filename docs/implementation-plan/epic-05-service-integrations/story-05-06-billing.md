# Story 5.6: Billing (Stripe)
**User Story:** As a Business Owner, I want to charge customers, so that the business is sustainable.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 5.6 from `docs/03`

## Technical Specification
**Goal:** Integrate Stripe Subscriptions.

**Changes Required:**
1.  **File:** `backend/src/services/billing.py`
    - `create_customer`, `create_checkout_session`.
2.  **File:** `backend/src/api/webhooks.py`
    - Handle `invoice.payment_succeeded`.
    - Verify signature.

## Acceptance Criteria
- [ ] Can create checkout session.
- [ ] Webhook updates DB status.

## Verification Plan
**Manual Verification:**
- Use Stripe CLI to forward webhooks to localhost. Trigger test payment.
