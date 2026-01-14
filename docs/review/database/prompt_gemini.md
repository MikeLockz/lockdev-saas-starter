# Database Codebase Review Prompt

**Role:** You are a Senior Database Architect and Security Engineer specializing in HIPAA-compliant SaaS architectures.

**Objective:** Conduct a comprehensive code review of the database layer in this repository (`backend/src/models`, `backend/migrations`, `docs/04 - sql.ddl`) to ensure adherence to the project's "Big Picture" goals, technical stack principles, and specific implementation plans.

## 1. Context & References
You must verify the code against the following documentation:
*   **Technical Overview:** `docs/tech-stack/00 - Overview.md`
    *   **Key Principles:** HIPAA compliant, Simple, Performant, AI-compatible.
    *   **Data Integrity:** ULID primary keys, UTC timestamps, Soft Deletes for clinical data.
    *   **Security:** Row Level Security (RLS), Audits by default (postgres trigger).
    *   **Architecture:** Multi-tenancy (Organization-based), Proxy Management (Many-to-Many), Granular Consent.
*   **Implementation Plan:** `docs/implementation-plan/**`
    *   **Epic 22 (Complete Billing):** Check for `billing_manager_id` on Patient, `managed_by_proxy_id` on BillingTransaction.
    *   **Epic 21 (User-Org):** Check for user-patient linking fields.
    *   **Epic 20 (Timezone):** Check for `timezone` columns on User and Organization.
    *   **Epic 14 (Proxies):** Check `patient_proxy_assignment` permissions.

## 2. Review Checklist

### A. HIPAA Compliance & Security
1.  **Row Level Security (RLS):** Are RLS policies defined/enabled for sensitive tables (`patients`, `appointments`, `documents`, etc.) to enforce tenant isolation?
2.  **Audit Logging:** Is the `audit_logs` table present? Are database triggers set up to automatically log `INSERT`, `UPDATE`, `DELETE` operations?
3.  **Privacy:** Are sensitive fields handled correctly? (e.g., `is_safe_for_voicemail` in contact methods).

### B. Data Model & Integrity
1.  **Primary Keys:** Are models using ULIDs (Universally Unique Lexicographically Sortable Identifier) as primary keys, stored as `UUID` type?
2.  **Time Handling:** Are all datetime fields using `TIMESTAMP WITH TIME ZONE` (UTC)?
3.  **Soft Deletes:** Do clinical entities (`Patient`, `Appointment`, `Document`, etc.) implement soft deletes (`deleted_at`) instead of hard deletes?
4.  **Constraints:** Are Foreign Keys, Unique Constraints, and Check Constraints properly defined to ensure data validity?

### C. Feature Specific Verification
1.  **Billing (Epic 22):** Verify `Patient` model has `billing_manager_id`. Verify `BillingTransaction` table exists and has `managed_by_proxy_id`.
2.  **Timezone (Epic 20):** Verify `Organization` and `User` models have `timezone` columns with correct defaults/nullability.
3.  **Proxies (Epic 14):** Verify `PatientProxyAssignment` model supports granular permissions (`can_view_clinical`, etc.).

### D. Code Quality (SQLAlchemy 2.0)
1.  **Modern Syntax:** Are models using the modern SQLAlchemy 2.0 syntax (`Mapped`, `mapped_column`)?
2.  **Typing:** Are Python type hints correct and comprehensive?
3.  **Migrations (Alembic):** Do migration scripts look idempotent and correct? Are there any "auto-generated" migrations that look messy or incomplete?

### E. Schema Consistency
1.  **DDL vs Models:** Does the actual SQLAlchemy code in `backend/src/models` match the reference design in `docs/04 - sql.ddl`? Note any discrepancies.

## 3. Deliverables
Produce a structured Markdown report with the following sections:

1.  **Executive Summary:** Pass/Fail assessment on HIPAA compliance and critical architecture goals.
2.  **Critical Issues:** Security gaps, missing audits, or data integrity risks.
3.  **Schema Discrepancies:** Differences between documentation and implementation.
4.  **Code Quality Observations:** Improvements for SQLAlchemy usage or migration safety.
5.  **Performance Recommendations:** Missing indexes or potential bottlenecks.

**Tone:** Strict, professional, and detail-oriented. Assume this report determines whether we go to production.
