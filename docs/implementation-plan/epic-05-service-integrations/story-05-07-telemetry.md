# Story 5.7: Behavioral Analytics
**User Story:** As a Product Manager, I want to track user behavior, so that we can improve the UX.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 5.7 from `docs/03`

## Technical Specification
**Goal:** Simple telemetry endpoint.

**Changes Required:**
1.  **Endpoint:** `POST /api/telemetry`.
2.  **Frontend Hook:** `useAnalytics`.

## Acceptance Criteria
- [ ] Events are logged with `event_type="analytics"`.

## Verification Plan
**Manual Verification:**
- Fire event from frontend. Check logs.
