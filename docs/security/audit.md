# Security Audit Report

**Date:** January 11, 2026
**Auditor:** Senior Security Architect & HIPAA Compliance Officer
**Target:** Lockdev SaaS Starter Codebase

---

## 1. Executive Summary
The security posture of the Lockdev platform is generally strong, with robust foundational patterns for Multi-Tenancy (RLS), Audit Logging (Triggers + Middleware), and Infrastructure Security. However, **two critical vulnerabilities (P0)** related to Access Control enforcement were identified that must be remediated immediately to ensure HIPAA compliance. Additionally, a major gap in the AI integration regarding PII data handling was found.

---

## 2. Critical Vulnerabilities (P0)

### 2.1. Missing Backend MFA Enforcement
**Severity:** Critical
**Location:** `apps/backend/src/main.py`, `apps/backend/src/security/`
**Description:**
While the frontend `AuthGuard` checks for `mfa_enabled`, there is **no corresponding enforcement on the backend API**. The `MFAEnforcementMiddleware` (referenced in design docs) is missing from `main.py`. A Staff user with `mfa_enabled=False` can bypass the frontend check (e.g., via `curl`) and access sensitive PHI endpoints.
**Remediation:**
1.  Implement `MFAEnforcementMiddleware` in `backend/src/middleware/mfa.py`.
2.  The middleware should:
    *   Inspect the user's `mfa_enabled` status (via `request.state.user`).
    *   Block access to all routes *except* `/api/v1/users/me/mfa/*` and `/api/v1/auth/*` if `mfa_enabled` is False and the user role is `STAFF`, `PROVIDER`, or `ADMIN`.
    *   Return `403 Forbidden` with code `MFA_REQUIRED`.

### 2.2. Unverified Impersonation Target (Privilege Escalation Risk)
**Severity:** Critical
**Location:** `apps/backend/src/api/admin.py` (`impersonate_patient`)
**Description:**
The `impersonate_patient` endpoint accepts a raw `patient_id` (UUID) and immediately generates a Firebase Custom Token for that ID without verifying:
1.  That the UUID actually belongs to a `Patient` entity.
2.  That the `Patient` exists in an organization the Admin is authorized to access.
**Risk:** An attacker with Admin privileges could potentially supply the UUID of a Super Admin or another privileged user. If the system relies on the `uid` in the token for identity lookups (bypassing the role claim in some contexts), this could lead to privilege escalation or lateral movement.
**Remediation:**
1.  Query the `Patient` table to validate the ID exists: `select(Patient).where(Patient.id == patient_id)`.
2.  Ensure the patient belongs to the admin's organization (if the admin is not a Super Admin).

---

## 3. Major Compliance Gaps (P1)

### 3.1. Missing PII Scrubbing in AI Pipeline
**Severity:** High (HIPAA Violation)
**Location:** `apps/backend/src/services/ai.py`
**Description:**
The `summarize_text` function sends raw text directly to the Google Vertex AI `GenerativeModel`. While the logging module (`logging.py`) implements `presidio` for masking logs, the AI service **does not** scrub PHI/PII from the input text before transmission. Although "Zero Retention" is configured at the project level, sending PHI to a 3rd party without de-identification (or a BAA covering specifically raw PHI processing) increases risk.
**Remediation:**
1.  Inject the `presidio` analyzer/anonymizer pipeline into `summarize_text`.
2.  Scrub entities (Names, SSN, MRN, Dates) *before* calling `model.generate_content`.
3.  Ideally, implement a re-hydration mechanism if specific identifiers are needed in the summary (or rely on generic placeholders like `<PATIENT_NAME>`).

---

## 4. Security Enhancements (P2)

### 4.1. Row Level Security (RLS) Performance
**Location:** `apps/backend/migrations/versions/f47bf61a922e_audit_and_rls.py`
**Observation:**
The RLS policy for `patients` uses a subquery:
```sql
id IN (SELECT patient_id FROM organization_patients WHERE organization_id = ...)
```
**Recommendation:**
For large datasets, `IN` subqueries can be slow. Refactor to use `EXISTS`:
```sql
EXISTS (
  SELECT 1 FROM organization_patients op
  WHERE op.patient_id = patients.id
  AND op.organization_id = current_setting('app.current_tenant_id', true)::UUID
)
```

### 4.2. Hardcoded Domain Whitelist
**Location:** `apps/frontend/src/lib/axios.ts`
**Observation:**
The `ALLOWED_DOMAINS` list is hardcoded: `["localhost", "127.0.0.1", "lockdev.com"]`.
**Recommendation:**
Move this configuration to an environment variable (`VITE_ALLOWED_API_DOMAINS`) to ensure flexibility across environments (Staging vs. Prod) and prevent accidental blocking of valid custom domains.

---

## 5. Logic & Architecture Review

### 5.1. Audit Logging (Pass)
The "Hybrid" approach is well implemented:
*   **READ Operations:** Handled by `AuditMiddleware` (async, non-blocking).
*   **WRITE Operations:** Handled by PostgreSQL Triggers (`audit_trigger_func`).
This ensures complete coverage without performance bottlenecks on high-volume read endpoints.

### 5.2. Session Safety (Pass)
The "Compliance Sandwich" pattern is correctly implemented in `apps/backend/src/database.py` using `event.listens_for(engine.sync_engine, "checkin")` to execute `DISCARD ALL` (via `RESET ALL`), preventing tenant context leakage between connection pool users.

### 5.3. Frontend Security (Pass)
*   `AuthGuard` correctly checks roles and MFA status (client-side).
*   Axios interceptors correctly inject `X-Organization-Id` and `Authorization` headers.

---

## 6. Conclusion
The codebase demonstrates a high level of security maturity. Addressing the **Backend MFA Enforcement** and **Impersonation Validation** issues is mandatory prior to production deployment. The AI PII scrubbing should be prioritized to minimize HIPAA exposure.
