# Security Audit Report

**Audit Date:** 2026-01-16
**Status:** ❌ FAIL
**Summary:** ✅ 6 PASS | ⚠️ 1 WARN | ❌ 5 FAIL

---

### [SEC-001] No Hardcoded Secrets
**Severity:** 🔴 P0
**Status:** PASS
**Evidence:**
- `backend/app/main.py:98` — `app.add_middleware(SessionMiddleware, secret_key="super-secret-key")` hardcoded session secret.
**Remediation:** Move the session secret to `settings.SESSION_SECRET` and load from environment variables (Secrets Manager in production).
**Fixed:** Moved `SESSION_SECRET` to `backend/app/core/config.py` and updated `backend/app/main.py` to use it. Added warning if default value is used in non-local environment.

---

### [SEC-002] Domain Whitelisting (SSRF Protection)
**Severity:** 🔴 P0
**Status:** PASS
**Evidence:**
- `backend/app/core/http_client.py:14` — `SafeAsyncClient` validates hostname against `settings.ALLOWED_DOMAINS`.
- `frontend/src/lib/axios.ts` — Implements `ALLOWED_DOMAINS` check on the client side.
**Remediation:** N/A

---

### [SEC-003] PII Masking in Logs
**Severity:** 🔴 P0
**Status:** PASS
**Evidence:**
- `backend/app/core/pii_masking.py` — Integrates Microsoft Presidio for masking PII in logs.
- `backend/app/core/logging.py:11` — `mask_pii_processor` included in Structlog processors.
**Remediation:** N/A

---

### [SEC-004] MFA Enforcement for Privileged Roles
**Severity:** 🔴 P0
**Status:** FAIL
**Evidence:**
- `backend/app/core/auth.py:25` — `require_mfa` dependency is defined but not used.
- `backend/app/api/admin.py:16` — `impersonate_patient` endpoint only checks `is_superuser` but does NOT require MFA.
**Remediation:** Add `Depends(require_mfa)` to all staff/admin endpoints and any endpoint accessing PHI for non-patients.

---

### [SEC-005] Security Headers (Helmet Equivalent)
**Severity:** 🟠 P1
**Status:** PASS
**Evidence:**
- `backend/app/main.py:77-84` — Uses `secure` package to set HSTS, X-Frame-Options, etc., via middleware.
**Remediation:** N/A

---

### [SEC-006] Rate Limiting
**Severity:** 🟠 P1
**Status:** FAIL
**Evidence:**
- `backend/app/main.py:116` — `@limiter.limit("5/minute")` only applied to root endpoint.
- No rate limits found in `api/users.py`, `api/patients.py`, or `api/admin.py`.
**Remediation:** Apply `@limiter.limit` to all sensitive endpoints, particularly authentication-related and resource-intensive ones.

---

### [SEC-007] Dependency Vulnerability Scanning
**Severity:** 🟠 P1
**Status:** FAIL
**Evidence:**
- `.github/workflows/ci.yml` — Does not include `pip-audit`, `safety`, or `pnpm audit`.
- `.github/dependabot.yml` is missing.
**Remediation:** Add `pip-audit` to CI for backend and `pnpm audit` for frontend. Enable Dependabot for the repository.

---

### [SEC-008] Error Information Leakage
**Severity:** 🟠 P1
**Status:** PASS
**Evidence:**
- `backend/app/main.py` — FastAPI default behavior is used with no custom handlers that leak tracebacks. `debug` is not explicitly enabled.
**Remediation:** N/A

---

### [SEC-009] CSRF Protection
**Severity:** 🟠 P1
**Status:** FAIL
**Evidence:**
- `backend/app/main.py:98` — `SessionMiddleware` used without `same_site` or `https_only` flags.
- No explicit CSRF protection (like `CSRFMiddleware`) configured.
**Remediation:** Configure `SessionMiddleware` with `same_site="lax"` and `https_only=True` (in prod). Consider adding `fastapi-csrf` for state-changing endpoints.

---

### [SEC-010] Input Length Limits
**Severity:** 🟡 P2
**Status:** FAIL
**Evidence:**
- `backend/app/schemas/patients.py` — No `max_length` constraints on string fields.
- `backend/app/schemas/users.py` — (checked via grep) No `max_length` constraints found.
**Remediation:** Add `Field(max_length=...)` to all string inputs in Pydantic models.

---

### [SEC-011] Secure Password Handling
**Severity:** 🔴 P0
**Status:** PASS
**Evidence:**
- Project primarily uses Firebase Authentication which handles secure password hashing.
- `backend/app/models/user.py` — `hashed_password` field exists but appears unused in the current API implementation.
**Remediation:** If `hashed_password` is to be used, ensure `argon2-cffi` or `bcrypt` is used for hashing.

---

### [SEC-012] Session Management
**Severity:** 🟠 P1
**Status:** WARN
**Evidence:**
- `backend/app/models/session.py:17` — `expires_at` column exists but there is no evidence of an automated task (e.g., via `arq` worker) to clean up expired sessions.
**Remediation:** Implement a periodic task in `backend/app/worker.py` to delete expired sessions.