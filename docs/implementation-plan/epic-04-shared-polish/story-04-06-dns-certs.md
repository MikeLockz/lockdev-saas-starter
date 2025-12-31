# Story 4.6: DNS & Certificates
**User Story:** As an Admin, I want a custom domain with HTTPS, so that users trust the site.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 4.6 from `docs/03`

## Technical Specification
**Goal:** Configure Route53 and Aptible Managed TLS.

**Changes Required:**
1.  **File:** `infra/aws/route53.tf`.
2.  **Manual:** Provision Endpoint in Aptible.

## Acceptance Criteria
- [ ] DNS records created in Terraform state.

## Verification Plan
**Manual Verification:**
- `tofu plan` shows Route53 records.
