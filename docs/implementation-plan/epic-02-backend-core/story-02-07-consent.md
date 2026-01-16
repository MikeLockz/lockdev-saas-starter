# Story 2.7: Consent & Terms Tracking
**User Story:** As a Compliance Officer, I want to ensure users sign TOS and HIPAA forms before accessing the system.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 2.7 from `docs/03`

## Technical Specification
**Goal:** Enforce consent signatures.

**Changes Required:**
1.  **Models:** `ConsentDocument`, `UserConsent`.
2.  **Middleware/Dependency:** `verify_latest_consents`
    - Check if User has signed latest version of `TOS` and `HIPAA`.
    - If not, raise `403 Consent Required`.
3.  **Endpoint:** `POST /api/consent` to sign documents.

## Acceptance Criteria
- [ ] Unsigned user gets 403 on protected routes.
- [ ] Signed user gets 200.
- [ ] Audit log captures IP and Timestamp of signature.

## Verification Plan
**Automated Tests:**
- Create user without consent -> Request -> 403.
- Sign consent -> Request -> 200.
