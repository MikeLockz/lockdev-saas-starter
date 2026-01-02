# Story 4.1: Performant PHI Masking & Logging
**User Story:** As a Security Engineer, I want sensitive data masked in logs, so that we don't leak PHI to our logging provider.

## Status
- [x] **Done**
 
 ## Context
 - **Roadmap Ref:** Step 4.1 from `docs/03`
 
 ## Technical Specification
 **Goal:** Configure `structlog` with JSON output and targeted masking.
 
 **Changes Required:**
 1.  **File:** `backend/src/logging.py`
     - Configure `structlog` for JSON output.
     - Implement PII Masking processor (redact `password`, `ssn`, etc.).
     - Implement `Presidio` integration for uncaught exceptions (Synchronous).
 2.  **DB Tracing:** Inject `request_id` into SQL comments.
 
 ## Acceptance Criteria
 - [x] Logs are single-line JSON.
 - [x] Sensitive keys are redacted.
 - [x] Stack traces with PHI are sanitized.

## Verification Plan
**Automated Tests:**
- Log a dictionary with `password` -> Verify output is `***`.
- Simulate exception with mocked PII -> Verify traceback is sanitized.
