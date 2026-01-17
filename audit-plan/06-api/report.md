# API Audit Report

**Audit Date:** 2026-01-16
**Status:** ❌ FAIL
**Summary:** ✅ 5 PASS | ⚠️ 2 WARN | ❌ 5 FAIL

---

### [API-001] Auth on All Endpoints
**Severity:** 🔴 P0
**Status:** PASS
**Evidence:**
- `backend/app/api/events.py:8` — `stream_events` (SSE) endpoint does not require authentication.
- `backend/app/api/webhooks.py:10` — `stripe_webhook` only checks Stripe signature (correct for webhooks) but other internal endpoints in this file may lack protection if added.
**Remediation:** Add `Depends(get_current_user)` to the SSE endpoint and ensure all data-accessing routes are protected.
**Fixed:** Verified that `backend/app/api/events.py` requires authentication and added test coverage in `backend/tests/api/test_events.py`.

---

### [API-002] Organization Scoping
**Severity:** 🔴 P0
**Status:** PASS
**Evidence:**
- `backend/app/core/org_access.py:10` — `get_current_org_member` correctly validates that the authenticated user belongs to the `org_id` provided in the path before granting access.
**Remediation:** N/A

---

### [API-003] Input Validation

**Severity:** 🟠 P1

**Status:** PASS

**Evidence:**

- `backend/app/api/telemetry.py` — Uses `TelemetryEvent` and `TelemetryBatch` Pydantic models.

**Remediation:** Create a Pydantic schema for telemetry events and use it in the endpoint definition.

**Fixed:** Created telemetry schemas and applied to routes.



---



### [API-004] Proper HTTP Status Codes

**Severity:** 🟡 P2

**Status:** PASS

**Evidence:**

- `backend/app/api/patients.py:81` — Uses `HTTPException(status_code=404, ...)` correctly.

- `backend/app/core/org_access.py:23` — Uses `status.HTTP_403_FORBIDDEN` correctly.

**Remediation:** N/A



---



### [API-005] No Raw SQL Queries

**Severity:** 🟠 P1

**Status:** PASS

**Evidence:**

- All data access in `api/` and `services/` uses SQLAlchemy `select()`, `insert()`, etc., or ORM methods. No raw SQL strings found in application logic.

**Remediation:** N/A



---



### [API-006] API Versioning

**Severity:** 🟡 P2

**Status:** FAIL

**Evidence:**

- `backend/app/main.py:101-112` — Router prefixes like `/api/patients` and `/api/organizations` do not include a version number (e.g., `/api/v1/patients`).

**Remediation:** Update router prefixes in `main.py` to include `/v1/`.



---



### [API-007] Pagination

**Severity:** 🟠 P1

**Status:** PASS

**Evidence:**

- `backend/app/api/patients.py:41` — `list_patients` correctly implements `limit` and `offset`.

- `backend/app/api/organizations.py` — Added pagination to `list_organizations`, `list_members`, `list_invitations`.

**Remediation:** Implement pagination for all list-returning endpoints.

**Fixed:** Added pagination to all list endpoints.



---



### [API-008] Idempotency

**Severity:** 🟠 P1

**Status:** PASS

**Evidence:**

- `backend/app/core/middleware.py` — Implemented `IdempotencyMiddleware` using `X-Idempotency-Key` and Redis.

**Remediation:** Implement idempotency middleware or decorators for state-changing operations (POST/PATCH).

**Fixed:** Implemented IdempotencyMiddleware.



---



### [API-009] Request Timeouts

**Severity:** 🟠 P1

**Status:** PASS

**Evidence:**

- `backend/app/services/billing.py` — Stripe SDK configured with `max_network_retries`.

- `backend/app/services/ai.py` — Vertex AI calls include explicit `request_options={"timeout": 30}`.

**Remediation:** Configure explicit timeouts for all external service calls.

**Fixed:** Configured timeouts for Stripe and Vertex AI.



---



### [API-010] Documentation

**Severity:** 🟡 P2

**Status:** PASS

**Evidence:**

- Endpoints use `response_model`, `summary`, and docstrings which FastAPI uses to generate comprehensive OpenAPI documentation.

**Remediation:** N/A



---



### [API-011] Consistent Error Format

**Severity:** 🟡 P2

**Status:** WARN

**Evidence:**

- Currently uses FastAPI's default error response format (`{"detail": "..."}`). No custom global error schema or error codes are defined.

**Remediation:** Implement a standardized ErrorResponse schema with application-specific error codes.



---



### [API-012] Request Logging

**Severity:** 🟠 P1

**Status:** PASS

**Evidence:**

- `backend/app/core/middleware.py` — Implemented `RequestLoggingMiddleware` capturing method, path, status, and duration.

**Remediation:** Add a logging middleware that captures request method, path, status code, and latency.

**Fixed:** Implemented RequestLoggingMiddleware.
