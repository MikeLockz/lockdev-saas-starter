# Story 2.1: Configuration & Secure HTTP Client
**User Story:** As a Developer, I want centralized configuration and a secure HTTP client, so that I prevent SSRF attacks and manage secrets properly.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 2.1 from `docs/03`

## Technical Specification
**Goal:** Implement `pydantic-settings` and a domain-whitelisted `httpx` client.

**Changes Required:**
1.  **File:** `backend/src/config.py`
    - Class `Settings(BaseSettings)`.
    - Fields for `DATABASE_URL`, `REDIS_URL`, `SENTRY_DSN`, etc.
2.  **File:** `backend/src/http_client.py`
    - Class `SafeAsyncClient` inheriting from `httpx.AsyncClient`.
    - **Logic:** `validate_url` function to check against `ALLOWED_DOMAINS` whitelist.
    - **Whitelist:** AWS services, Google Identity, Stripe, etc.
    - **Timeout:** Default 10s.

## Acceptance Criteria
- [ ] Env vars load correctly.
- [ ] `SafeAsyncClient` raises `ValueError` for `http://evil.com`.
- [ ] `SafeAsyncClient` allows `https://identitytoolkit.googleapis.com`.

## Verification Plan
**Automated Tests:**
- Unit test mocking `httpx` to verify whitelist logic.
- Test loading config with missing env vars (should fail).
