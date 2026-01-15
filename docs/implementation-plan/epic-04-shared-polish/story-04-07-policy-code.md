# Story 4.7: Policy as Code (Checkov)
**User Story:** As a Security Engineer, I want to scan infrastructure code for misconfigurations, so that we don't deploy vulnerabilities.

## Status
- [x] **Complete**

## Context
- **Roadmap Ref:** Step 4.7 from `docs/03`

## Technical Specification
**Goal:** Add Checkov to CI.

**Changes Required:**
1.  **File:** `.github/workflows/infra-scan.yml`.

## Acceptance Criteria
- [x] CI fails if S3 bucket is unencrypted.

## Verification Plan
**Manual Verification:**
- Create a bad TF file (public bucket). Run checkov locally. Ensure it fails.
