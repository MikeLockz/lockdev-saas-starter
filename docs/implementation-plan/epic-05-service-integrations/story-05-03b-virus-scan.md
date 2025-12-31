# Story 5.3b: Virus Scanning (AWS Lambda)
**User Story:** As a Security Engineer, I want all uploads scanned for malware, so that the platform remains safe.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 5.3b from `docs/03`

## Technical Specification
**Goal:** Deploy Virus Scan Lambda.

**Changes Required:**
1.  **Infra:** `infra/aws/lambda-virus-scan.tf`
    - Lambda + ClamAV layer.
    - S3 Event Trigger.
    - Quarantine bucket logic.

## Acceptance Criteria
- [ ] EICAR test file is moved to quarantine.
- [ ] Clean file is tagged `scan-status=clean`.

## Verification Plan
**Manual Verification:**
- Upload EICAR file. Verify it moves to quarantine bucket.
