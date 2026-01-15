# Story 4.5: Aptible Deployment
**User Story:** As an SRE, I want a deployment pipeline, so that code goes to production reliably.

## Status
- [x] **Complete**

## Context
- **Roadmap Ref:** Step 4.5 from `docs/03`

## Technical Specification
**Goal:** Configure `Procfile` and GitHub Actions.

**Changes Required:**
1.  **File:** `Procfile` (web, worker, release).
2.  **File:** `.github/workflows/deploy.yml`
    - Decrypt secrets (`sops`).
    - Sync config (`aptible config:set`).
    - Deploy code (`git push`).

## Acceptance Criteria
- [x] CI pipeline runs successfully (dry run).

## Verification Plan
**Manual Verification:**
- Review Action logs.
