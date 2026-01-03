# Story 15.1: Billing API
**User Story:** As an Organization Admin, I want to start a checkout session to subscribe.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 4.2 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Billing")
- **Existing:** Billing service exists in `backend/src/services/billing.py`

## Technical Specification
**Goal:** Implement Stripe checkout session creation and portal access.

**Changes Required:**

1.  **Config:** `backend/src/config.py`
    - Ensure `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
    - Add `STRIPE_PRICE_IDS` (dict of plan prices)
    - Add `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL`

2.  **Schemas:** `backend/src/schemas/billing.py` (NEW)
    - `CheckoutSessionRequest` (price_id, quantity?)
    - `CheckoutSessionResponse` (session_id, url)
    - `SubscriptionStatus` (status, plan, current_period_end, cancel_at_period_end)
    - `PortalSessionResponse` (url)

3.  **API Router:** `backend/src/api/billing.py` (NEW)
    - `POST /api/v1/organizations/{org_id}/billing/checkout`
      - Create Stripe customer if not exists
      - Create checkout session
      - Return session URL for redirect
    - `GET /api/v1/organizations/{org_id}/billing/subscription`
      - Return current subscription status
    - `POST /api/v1/organizations/{org_id}/billing/portal`
      - Create Stripe billing portal session
      - For managing payment methods, invoices

4.  **Service Update:** `backend/src/services/billing.py`
    - `create_checkout_session(org_id, price_id)`
    - `get_subscription_status(org_id)`
    - `create_portal_session(org_id)`

## Acceptance Criteria
- [ ] `POST /billing/checkout` returns Stripe session URL.
- [ ] Stripe customer created/linked to organization.
- [ ] `GET /billing/subscription` returns current status.
- [ ] `POST /billing/portal` returns portal URL.
- [ ] Audit log captures billing actions.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_billing.py` (mocked Stripe)

**Manual Verification:**
- Create checkout session, complete in Stripe test mode.
