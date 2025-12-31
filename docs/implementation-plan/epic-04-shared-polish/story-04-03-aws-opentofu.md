# Story 4.3: OpenTofu AWS Setup
**User Story:** As an Ops Engineer, I want infrastructure as code, so that environments are reproducible.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 4.3 from `docs/03`

## Technical Specification
**Goal:** Provision S3, SES, Route53, and Secrets Manager.

**Changes Required:**
1.  **Directory:** `infra/aws/`
2.  **Files:**
    - `main.tf`, `variables.tf`.
    - `s3.tf` (Encrypted, Private).
    - `ses.tf` (Domain Identity, DKIM).
    - `secrets.tf` (GCP Credentials).
    - `backend.tf` (S3 State + DynamoDB Lock).

## Acceptance Criteria
- [ ] `tofu init` and `tofu plan` succeed.
- [ ] State is stored in S3.

## Verification Plan
**Manual Verification:**
- Run `tofu plan`. Verify resource list matches expectations.
