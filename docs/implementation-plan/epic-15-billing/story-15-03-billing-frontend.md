# Story 15.3: Billing Frontend
**User Story:** As an Organization Admin, I want a UI to view and manage my subscription.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 4.2 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Routes: `/admin/billing`)

## Technical Specification
**Goal:** Implement billing management UI.

**Changes Required:**

1.  **Routes:** `frontend/src/routes/_auth/admin/`
    - `billing.tsx` - Billing management page

2.  **Components:** `frontend/src/components/billing/`
    - `SubscriptionCard.tsx`
      - Current plan name and status badge
      - Price and billing period
      - Next billing date
      - Cancel/upgrade buttons
    - `PlanSelector.tsx`
      - Available plans comparison
      - Feature list per plan
      - Subscribe/upgrade buttons
    - `InvoiceHistory.tsx`
      - List of past invoices
      - Download PDF links
    - `PaymentMethodCard.tsx`
      - Current payment method (last 4 digits)
      - Link to Stripe portal for updates

3.  **Hooks:** `frontend/src/hooks/api/`
    - `useSubscription.ts` - Current subscription status
    - `useCreateCheckout.ts` - Start checkout mutation
    - `useBillingPortal.ts` - Get portal URL

4.  **Integration:**
    - Redirect to Stripe checkout for new subscription
    - Redirect to Stripe portal for management
    - Show upgrade prompts if on free tier

## Acceptance Criteria
- [ ] `/admin/billing` displays current subscription.
- [ ] Subscribe button redirects to Stripe checkout.
- [ ] Manage button redirects to Stripe portal.
- [ ] Status badge shows ACTIVE/PAST_DUE/CANCELLED.
- [ ] Admin role required to access billing.

## Verification Plan
**Automated Tests:**
- `pnpm test -- SubscriptionCard`

**Manual Verification:**
- Navigate to /admin/billing
- Click subscribe, complete checkout in Stripe
- Verify status updates after payment
