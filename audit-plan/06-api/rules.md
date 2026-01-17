# API Audit Rules

## Scope
- `backend/src/api/` — FastAPI routers
- `backend/src/security/` — Auth dependencies
- `backend/src/models/` — Pydantic schemas

---

## Rules

### API-001: Auth on All Endpoints
**Severity:** 🔴 P0  
**Requirement:** All endpoints except `/health` and `/docs` must require authentication.  
**Check:**
```bash
# Find endpoints without auth dependency
grep -rE "@(router|app)\.(get|post|put|delete|patch)" backend/src/api/ | grep -v "Depends.*get_current"
```
**Expected:** All data endpoints use `Depends(get_current_user)` or similar.

---

### API-002: Organization Scoping
**Severity:** 🔴 P0  
**Requirement:** All data queries must be scoped to the current user's organization(s).  
**Rationale:** Prevents cross-tenant data access.  
**Check:**
```bash
grep -r "organization_id" backend/src/api/
grep -r "current_tenant_id\|get_auth_context" backend/src/api/
```
**Expected:** Queries filter by organization from auth context.

---

### API-003: Input Validation
**Severity:** 🟠 P1  
**Requirement:** All request bodies must use Pydantic models for validation.  
**Check:**
```bash
# Find endpoints accepting raw dict or Any
grep -rE "def.*\(.*:\s*(dict|Dict|Any)" backend/src/api/
```
**Expected:** No matches. All inputs typed with Pydantic models.

---

### API-004: Proper HTTP Status Codes
**Severity:** 🟡 P2  
**Requirement:** Endpoints must return appropriate status codes (401, 403, 404, 422).  
**Check:**
```bash
grep -r "HTTPException\|status_code" backend/src/api/
grep -r "status.HTTP_401\|status.HTTP_403\|status.HTTP_404" backend/src/api/
```
**Expected:** Proper differentiation between auth (401), authz (403), and not found (404).

---

### API-005: No Raw SQL Queries
**Severity:** 🟠 P1  
**Requirement:** Application code must use SQLAlchemy ORM, not raw SQL strings.  
**Rationale:** Prevents SQL injection vulnerabilities.  
**Check:**
```bash
grep -rE "execute\(.*SELECT|execute\(.*INSERT|execute\(.*UPDATE|execute\(.*DELETE" backend/src/api/ backend/src/services/
grep -r "text\(" backend/src/api/
```
**Exceptions:** Migrations and database setup files.

---

## General Best Practices

### API-006: API Versioning
**Severity:** 🟡 P2  
**Requirement:** API must have versioning strategy (URL path or header).  
**Check:**
```bash
grep -r "/v1/\|/api/v" backend/src/api/ backend/src/main.py
grep -r "X-API-Version\|Accept-Version" backend/src/
```

---

### API-007: Pagination
**Severity:** 🟠 P1  
**Requirement:** List endpoints must support pagination to prevent unbounded result sets.  
**Check:**
```bash
grep -r "limit\|offset\|page\|cursor" backend/src/api/
grep -r "skip\|take\|PaginatedResponse" backend/src/
```

---

### API-008: Idempotency
**Severity:** 🟠 P1  
**Requirement:** Non-GET endpoints should support idempotency keys for safe retries.  
**Check:**
```bash
grep -r "Idempotency-Key\|idempotency" backend/src/
```
**Critical Endpoints:** Payment processing, resource creation

---

### API-009: Request Timeouts
**Severity:** 🟠 P1  
**Requirement:** External API calls must have explicit timeouts.  
**Check:**
```bash
grep -r "timeout\|Timeout" backend/src/services/
grep -r "httpx.*timeout\|aiohttp.*timeout" backend/src/
```

---

### API-010: Documentation
**Severity:** 🟡 P2  
**Requirement:** All endpoints must have OpenAPI documentation with examples.  
**Check:**
```bash
grep -r "summary=\|description=\|response_model" backend/src/api/
grep -r "Example\|example=" backend/src/schemas/
```
**Verify:** Access `/docs` endpoint.

---

### API-011: Consistent Error Format
**Severity:** 🟡 P2  
**Requirement:** All errors must return consistent JSON format with error code, message, and details.  
**Check:**
```bash
grep -r "ErrorResponse\|error_code\|detail" backend/src/
grep -r "exception_handler" backend/src/main.py
```

---

### API-012: Request Logging
**Severity:** 🟠 P1  
**Requirement:** All requests must be logged with correlation ID, method, path, status, and duration.  
**Check:**
```bash
grep -r "request_id\|X-Request-ID\|correlation" backend/src/middleware/
grep -r "duration\|elapsed\|latency" backend/src/
```
