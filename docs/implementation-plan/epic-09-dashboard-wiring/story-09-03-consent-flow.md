# Story 9.3: Consent Flow Completion
**User Story:** As a Compliance Officer, I want users blocked from PHI routes until they sign consent, so that we meet HIPAA requirements.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 1.1.5 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Consent & Compliance")
- **Backend:** Consent endpoints already exist

## Technical Specification
**Goal:** Complete the consent flow UI and integrate with backend APIs.

**Changes Required:**

1.  **Route:** `frontend/src/routes/consent.tsx`
    - Fetch required consents from API
    - Display list of documents to sign
    - Each document: Title, content preview, checkbox
    - "I Agree" button sends POST for each document
    - Redirect to dashboard on completion

2.  **Components:** `frontend/src/components/consent/`
    - `ConsentDocument.tsx` - Single document display
      - Title, last updated, content (scrollable)
      - Checkbox to acknowledge
    - `ConsentList.tsx` - List of required documents

3.  **Hooks:** `frontend/src/hooks/`
    - `useRequiredConsents.ts` - GET /api/v1/consent/required
    - `useSignConsent.ts` - POST /api/v1/consent

4.  **Auth Guard Update:** `frontend/src/components/auth-guard.tsx`
    - Check `requires_consent` flag from user profile
    - Redirect to `/consent` if true

5.  **Flow:**
    - User logs in → Auth Guard checks consent
    - If `requires_consent = true` → Redirect to `/consent`
    - User signs all documents → API updates flag
    - Redirect to `/dashboard`

## Acceptance Criteria
- [x] User with pending consent redirected to `/consent`.
- [x] Consent page shows all required documents.
- [x] Signing document sends POST to API.
- [x] After all signed, user redirected to dashboard.
- [x] User cannot bypass consent route.
- [x] Audit log captures consent signature.

## Verification Plan
**Automated Tests:**
- `pnpm test -- ConsentList` (component test)
- Playwright E2E: New user consent flow

**Manual Verification:**
- Create new user (requires_consent = true)
- Login, verify redirect to consent
- Sign documents, verify redirect to dashboard
- Verify audit log entries
