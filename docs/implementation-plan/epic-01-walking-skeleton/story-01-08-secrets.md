# Story 1.8: Secrets Management
**User Story:** As a Developer, I want to manage secrets securely, so that I don't accidentally commit credentials.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 1.8 from `docs/03`

## Technical Specification
**Goal:** Setup SOPS and `.env` patterns.

**Changes Required:**
1.  **File:** `.sops.yaml` configuration.
2.  **File:** `.env.example`
    - Template for all required env vars (DB, Redis, AWS, Firebase).
    - **CRITICAL:** Include `ALLOWED_DOMAINS` and `ALLOWED_HOSTS`.

## Acceptance Criteria
- [ ] `.env.example` covers all config needed for Docker Compose.
- [ ] `sops` encryption works (if keys are available).

## Verification Plan
**Manual Verification:**
- Copy `.env.example` to `.env`.
- Verify `docker compose up` still works with the new env file.
