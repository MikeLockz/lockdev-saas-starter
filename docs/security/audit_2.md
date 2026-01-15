# Security Audit Report

**Date:** January 11, 2026
**Target:** `lockdev-saas-starter` Codebase
**Auditor:** AI Security Agent

---

## 1. Executive Summary

The `lockdev-saas-starter` exhibits a strong security posture with a "Security by Design" approach. Key strengths include robust JWT validation, comprehensive Row-Level Security (RLS) foundations, and synchronous PII masking in logs.

However, **critical vulnerabilities** exist in the Audit Logging coverage (missing PHI endpoints) and Business Logic (Appointment race conditions). The Tenant Context setting mechanism is reliant on route dependencies, which creates a "fail-open" risk if developers forget to include `get_current_org_member` in future endpoints.

**Overall Score:** B+

---

## 2. Vulnerability Findings

| Severity | Category | Location | Description | Remediation |
| :--- | :--- | :--- | :--- | :--- |
| **P0** | **Audit Gap** | `backend/src/middleware/audit.py` | **Incomplete PHI Read Logging.** The audit middleware uses a strict allow-list of regex patterns (`/api/staff`, `/api/patients`). It **fails to log** read access to other PHI-rich endpoints like `/api/.../appointments`, `/messages`, and `/calls`. Accessing these resources currently leaves no trace in `audit_logs`. | Update `SENSITIVE_PATTERNS` to include all PHI routes or switch to an "Audit by Default" strategy for all `/api/organizations/*` GET requests. |
| **P1** | **Race Condition** | `backend/src/api/appointments.py` (Ln 120) | **Appointment Double-Booking.** The `create_appointment` logic performs a `SELECT` to check availability followed by an `INSERT` ("Check-then-Act"). Concurrent requests can pass the check simultaneously, resulting in double-booked slots. | Implement a **locking strategy**. Use `SELECT ... FOR UPDATE` on the `Provider` row to serialize booking requests for the same provider, or add a PostgreSQL Exclusion Constraint. |
| **P1** | **Privilege Escalation** | `backend/src/api/admin.py` | **Impersonation Scope Risk.** `impersonate_patient` accepts a raw `patient_id` UUID and mints a token. It does not strictly verify the target UUID belongs to a `Patient` entity. If a Super Admin ID is supplied, it generates a valid token for that admin (lateral movement). | Add a database check to ensure `patient_id` exists in the `patients` table *before* minting the token. |
| **P2** | **Context Safety** | `backend/src/security/auth.py` | **Missing Tenant Context in Base Auth.** `get_current_user` sets `user_id` context but leaves `tenant_id` context empty. Endpoints relying solely on this dependency will execute with `app.current_tenant_id = NULL`, potentially bypassing RLS policies if not strictly written. | Update `get_current_user` to read `X-Organization-Id` header (if available) or ensure RLS policies strictly fail on NULL tenant ID. |

---

## 3. Detailed Analysis

### 3.1 Authentication & Identity
*   **Strengths:**
    *   Firebase Admin SDK correctly validates JWT signatures and expiration.
    *   Mock authentication is securely gated behind `ENVIRONMENT != "local"` checks.
    *   Session tracking (`UserSession`) is correctly implemented with `last_active_at` updates.
*   **Weaknesses:**
    *   The Impersonation flow ("Break Glass") in `admin.py` generates custom tokens. While functionally correct, it lacks strict type checking on the target resource, allowing potential token generation for non-patient entities.

### 3.2 Authorization & Multi-Tenancy
*   **Strengths:**
    *   RLS context variables (`app.current_user_id`, `app.current_tenant_id`) are correctly injected via `sqlalchemy.event` hooks in `database.py`.
    *   `org_access.py` dependency correctly enforces membership and sets the tenant context.
*   **Weaknesses:**
    *   Tenant context setting is coupled to the `get_current_org_member` dependency. If a developer creates a new endpoint using only `get_current_user`, the database session will have no tenant context. This requires RLS policies to be written defensively (e.g., `tenant_id IS NOT NULL`).

### 3.3 Data Privacy & HIPAA
*   **Strengths:**
    *   `logging.py` implements a robust masking strategy using `mask_sensitive_keys` and synchronous `Presidio` analysis for exception tracebacks. This effectively prevents PHI leaks in error logs.
    *   AWS S3 buckets are configured with Encryption (`AES256`) and Public Access Blocks.
*   **Weaknesses:**
    *   The `AuditMiddleware` is brittle. It relies on manual regex matching. As the API grows (e.g., adding `/lab-results`), these endpoints will be unaudited by default.

### 3.4 Infrastructure
*   **Strengths:**
    *   Terraform/OpenTofu configs enforce best practices: Encryption at rest, Versioning, and Access Logging for S3.
    *   CORS configuration is restrictive and appropriate.

---

## 4. Code Hardening Suggestions

1.  **Database Locking for Appointments:**
    ```python
    # In create_appointment
    # Lock the provider row to serialize bookings
    await db.execute(
        select(Provider).where(Provider.id == data.provider_id).with_for_update()
    )
    # Now check for overlap and insert...
    ```

2.  **Robust Audit Middleware:**
    Change the middleware logic to audit **ALL** GET requests starting with `/api/organizations/` (excluding specific allow-listed paths like public config), rather than trying to allow-list specific sensitive paths.

3.  **Strict RLS Policies:**
    Ensure all PostgreSQL RLS policies use `CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid)`. This ensures that if the context is NULL, the query fails or returns nothing, rather than defaulting to a permissive state.

4.  **Impersonation Verification:**
    ```python
    # In impersonate_patient
    # Verify target is actually a patient
    patient = await db.get(Patient, pid)
    if not patient:
        raise HTTPException(404, "Patient not found")
    # Proceed to mint token...
    ```
