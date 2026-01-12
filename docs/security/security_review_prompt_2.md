# Comprehensive Security Audit Prompt

**Role:** You are a Principal Security Researcher and Penetration Tester specializing in HIPAA-compliant healthcare architectures. You have deep expertise in Python (FastAPI), TypeScript (React), AWS, and Container Security.

**Objective:** Conduct a deep-dive white-box security audit of the entire `lockdev-saas-starter` codebase. Your goal is to find critical vulnerabilities, logic flaws, and compliance violations that standard automated tools might miss.

**Target Scope:**
- **Backend:** `apps/backend/src/` (FastAPI, SQLAlchemy, Auth logic)
- **Frontend:** `apps/frontend/src/` (React, Auth handling, Data binding)
- **Infrastructure:** `infra/` (OpenTofu/Terraform, Docker configs)
- **Configuration:** `*.toml`, `*.json`, `Makefile`, `.github/`

---

## 1. Authentication & Identity Architecture
**Focus:** `apps/backend/src/security/`, `apps/backend/src/api/auth.py`

*   **JWT Validation:** Scrutinize `verify_token` dependencies. Are the signing keys rotated? Is the `aud` (audience) and `iss` (issuer) strictly checked against Firebase/GCIP configs?
*   **MFA Bypass:** Analyze the `mfa_required` dependency. Can a user with `mfa_enabled=False` access endpoints decorated with `@requires_mfa`? Is there a race condition in the setup flow?
*   **Session Management:** Check `Revoke Session` logic. Does deleting a session in the DB actually invalidate the JWT (via a blacklist check or short expiry)?
*   **Impersonation:** Review the "Break Glass" logic in `apps/backend/src/api/admin.py`. Is the `act_as` claim cryptographically bound to the token? Can an admin impersonate a Super Admin?

## 2. Authorization & Multi-Tenancy (IDOR/RLS)
**Focus:** `apps/backend/src/middleware/`, `apps/backend/src/database.py`, `apps/backend/src/api/`

*   **Row Level Security (RLS):** Inspect the `set_session_context` hook in `database.py`. Is `app.current_tenant_id` reliably set for *every* request? Can it be spoofed by a malicious header?
*   **Tenant Leakage:** Search for queries utilizing `select(...)` that *miss* the `where(organization_id=...)` clause.
*   **IDOR:** Look at endpoints like `GET /patients/{id}`. Does the code verify that `{id}` belongs to the `current_user.organization_id`?
*   **Role Escalation:** Can a `STAFF` member modify `PROVIDER` resources? Check the `RoleGuard` logic on both Frontend and Backend.

## 3. Data Privacy & HIPAA Compliance
**Focus:** `apps/backend/src/logging.py`, `apps/backend/src/models/`, `audit_logs`

*   **PHI Leakage (Logs):** Search for `print()`, `console.log()`, or unstructured logger calls that might dump Patient objects or Pydantic models containing PHI.
*   **Presidio Scrubbing:** Audit the `logging.py` configuration. Are the PII recognizers active? Is the fallback safe?
*   **Audit Trail:** Verify that the `AuditMiddleware` captures *read* access to PHI. Is the `audit_logs` table truly immutable?
*   **Data Retention:** Check `DELETE` endpoints. Do they use soft-deletes (`deleted_at`) consistently? Are "Right to be Forgotten" requests (`POST /export`) implemented securely?

## 4. Input Validation & Injection Attacks
**Focus:** `apps/backend/src/schemas/`, SQL Queries

*   **SQL Injection:** Look for raw SQL usage (`text(...)`) in SQLAlchemy. Are parameters bound correctly, or are f-strings used (Danger!)?
*   **XSS (Frontend):** Check React components for `dangerouslySetInnerHTML`. Validate that user inputs (notes, messages) are sanitized.
*   **Mass Assignment:** Check Pydantic models for `extra='allow'`. Can a user inject fields like `is_super_admin` during a profile update?

## 5. Infrastructure & Cloud Security
**Focus:** `infra/aws/`, `docker-compose.yml`, `.github/workflows/`

*   **S3 Buckets:** specific check for `acl = "public-read"` or missing `server_side_encryption_configuration`.
*   **IAM Policies:** Review `infra/aws/iam.tf`. Are policies overly permissive (`Action: "*"`, `Resource: "*"` )?
*   **Secrets:** Scan for hardcoded credentials in `docker-compose.yml` or defaults in `config.py` that might accidentally be used in production.
*   **Container Security:** Check `Dockerfile`s. Are they running as `root`? Are base images pinned to SHA digests?

## 6. Logic & Business Flow Vulnerabilities
**Focus:** `apps/backend/src/services/`

*   **Race Conditions:** specific check on `Appointment` booking. Can two users book the same slot simultaneously? (Look for `FOR UPDATE` locks).
*   **Safe Contact Protocol:** Review `services/notifications.py`. Is the `is_safe_for_voicemail` flag *always* checked before sending SMS/Voice?
*   **Payment State:** Can a user access paid features after a subscription `invoice.payment_failed` webhook is received?

---

## Output Deliverable

Provide a **Markdown Security Report** containing:

1.  **Executive Summary:** High-level posture assessment (Score: A-F).
2.  **Vulnerability List (Table):**
    *   **Severity:** Critical, High, Medium, Low.
    *   **Category:** (e.g., Auth Bypass, IDOR, Info Leak).
    *   **Location:** File path & Line number.
    *   **Description:** Technical proof of concept or reasoning.
    *   **Remediation:** Specific code fix or config change.
3.  **Code Hardening Suggestions:** Non-critical improvements (e.g., "Add Content-Security-Policy headers").
4.  **Positive Findings:** Controls that are implemented correctly (e.g., "RLS implementation is robust").

**Start by analyzing the authentication flow in `apps/backend/src/security/auth.py` and the database session logic in `apps/backend/src/database.py`.**
