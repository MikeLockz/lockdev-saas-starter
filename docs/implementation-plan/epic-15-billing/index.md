# Epic 15: Billing (Stripe)
**User Story:** As an Organization Admin, I want to manage subscriptions and billing, so that I can pay for the service.

**Goal:** Stripe integration for subscription management with checkout and webhook handling.

## Traceability Matrix
| Plan Step (docs/10) | Story File | Status |
| :--- | :--- | :--- |
| Step 4.2 (API) | `story-15-01-billing-api.md` | ✅ Complete |
| Step 4.2 (Webhooks) | `story-15-02-stripe-webhooks.md` | ✅ Complete |
| Step 4.2 (Frontend) | `story-15-03-billing-frontend.md` | ✅ Complete |

## Execution Order
1.  [x] `story-15-01-billing-api.md`
2.  [x] `story-15-02-stripe-webhooks.md`
3.  [x] `story-15-03-billing-frontend.md`

## Epic Verification
**Completion Criteria:**
- [x] Stripe checkout session created successfully.
- [x] Webhook handles invoice.paid event.
- [x] Subscription status updates in database.
- [x] Billing UI displays current plan.
- [x] Can upgrade/downgrade subscription.
