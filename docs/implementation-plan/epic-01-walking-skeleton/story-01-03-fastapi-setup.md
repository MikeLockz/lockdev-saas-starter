# Story 1.3: FastAPI App with Middleware
**User Story:** As a Backend Developer, I want a production-ready FastAPI application shell, so that I have security, observability, and health checks from day one.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 1.3 from `docs/03`
- **Docs Ref:** `docs/05 - API Reference.md` (Health Checks)

## Technical Specification
**Goal:** Create `src/main.py` with full middleware stack.

**Changes Required:**
1.  **File:** `backend/src/config.py` (Minimal)
    - Settings for `SENTRY_DSN`, `ENVIRONMENT`, `ALLOWED_HOSTS`, `FRONTEND_URL`.
2.  **File:** `backend/src/main.py`
    - Initialize `FastAPI`.
    - **Sentry SDK** initialization.
    - **Middleware:**
        1. `TrustedHostMiddleware`
        2. `CORSMiddleware`
        3. `SecurityHeadersMiddleware` (using `secure` library)
        4. `RequestIDMiddleware` (Custom - injects `X-Request-ID`)
        5. `SlowAPIMiddleware` (Rate Limiting)
        6. `GZipMiddleware`
    - **Endpoints:**
        - `GET /health` (Shallow)
        - `GET /health/deep` (Deep - mock DB/Redis for now, or catch errors)

## Acceptance Criteria
- [ ] App starts with `uvicorn`.
- [ ] `GET /health` returns 200 OK.
- [ ] Responses include `X-Request-ID` and Security headers.

## Verification Plan
**Manual Verification:**
- Command: `cd backend && uv run uvicorn src.main:app --reload`
- Request: `curl -v http://localhost:8000/health`
- Expected: 200 OK, Headers present.
