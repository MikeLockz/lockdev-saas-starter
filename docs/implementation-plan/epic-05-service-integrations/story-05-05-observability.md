# Story 5.5: Observability (CloudWatch)
**User Story:** As an Ops Engineer, I want centralized logs, so that I can debug production issues.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 5.5 from `docs/03`

## Technical Specification
**Goal:** Ensure logs are shipped to CloudWatch (via Aptible).

**Changes Required:**
1.  **Config:** Verify `structlog` JSON output (completed in Epic 4).
2.  **Platform:** Configure Aptible Log Drain (Manual/TF).

## Acceptance Criteria
- [ ] Logs appear in CloudWatch.

## Verification Plan
**Manual Verification:**
- Generate logs. Check AWS CloudWatch Console.
