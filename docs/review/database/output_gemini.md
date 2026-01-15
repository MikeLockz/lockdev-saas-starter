# Database Codebase Review Report

**Date:** January 13, 2026
**Status:** **FAIL** (Requires immediate remediation for HIPAA and Architecture compliance)

## 1. Executive Summary
While the database layer follows SQLAlchemy 2.0 modern syntax and implements many core principles (UTC timestamps, basic RLS, Audit Logging), there are critical failures in adhering to the project's "Big Picture" goals. Most notably, several newer clinical and billing entities bypass Soft Delete requirements and ULID primary key standards. Security coverage (RLS and Audits) is inconsistent across the latest feature implementations (Epic 22).

## 2. Critical Issues

### A. Data Integrity: ULID Standards Violation
The project mandate requires **ULID primary keys** (stored as UUID) for all entities.
- **Failures:** `MessageThread`, `Message`, `Notification`, `BillingTransaction`, `SubscriptionOverride`, `UserSession`, and `UserDevice` all use `gen_random_uuid()` (standard UUIDv4) instead of the `UUIDMixin`.
- **Impact:** Breaks lexicographical sortability and consistency across the data model.

### B. Compliance: Soft Delete Omissions
The technical overview mandates **Soft Deletes** for all clinical data.
- **Failures:** `Appointment` and `Document` (core clinical entities) do NOT implement `SoftDeleteMixin`.
- **Impact:** Accidental hard deletes of clinical data will result in permanent loss of PHI and audit trail gaps, a major HIPAA risk.

### C. Security: Incomplete RLS & Audit Coverage
Defense-in-depth requires RLS and Audits on all sensitive tables.
- **Failures:** 
    - `billing_transactions` and `subscription_overrides` have NO Row Level Security (RLS) policies and NO Audit Triggers.
    - `support_tickets`, `calls`, and `tasks` are missing Audit Triggers.
- **Impact:** Potential for unauthorized access to financial data and lack of accountability for billing/operational changes.

### D. Privacy: Contact Method Implementation
- **Success:** `ContactMethod` correctly implements `is_safe_for_voicemail`.
- **Observation:** Ensure application logic strictly enforces this flag before IVR/Voice operations.

## 3. Schema Discrepancies

| Entity | Documentation (`04 - sql.ddl`) | Implementation (`src/models`) | Discrepancy |
| --- | --- | --- | --- |
| **Org Members** | `organization_memberships` | `OrganizationMember` | Class name vs Table name inconsistency. |
| **Care Team** | `deleted_at` (Implied) | `removed_at` | Uses custom field instead of standard `SoftDeleteMixin`. |
| **Billing** | Not in DDL | Implemented (Epic 22) | DDL is out of date with current implementation. |

## 4. Code Quality Observations (SQLAlchemy 2.0)
- **Typing:** Generally excellent. Use of `Mapped` and `mapped_column` is consistent and idiomatic.
- **Mixins:** `UUIDMixin`, `TimestampMixin`, and `SoftDeleteMixin` are well-designed but underutilized in recent migrations.
- **Migrations:** Migration `l6m7n8o9p0q1_billing_tables.py` follows a manual SQL style rather than leveraging model definitions, leading to the omissions noted in Critical Issues.

## 5. Performance Recommendations
- **Indexes:** 
    - Add index to `audit_logs(resource_id)` to speed up history lookups for specific entities.
    - Add index to `billing_transactions(created_at DESC)` (Already present, good).
- **RLS Performance:** The `patient_isolation` policy uses a subquery on `organization_patients`. For high-volume tenants, consider a flattened `organization_id` column on the `patients` table (redundant but faster for RLS).

## 6. Action Plan
1.  **Refactor:** Apply `SoftDeleteMixin` to `Appointment`, `Document`, `MessageThread`, and `Message`.
2.  **Standardize:** Migrate `gen_random_uuid()` columns to use `ulid` defaults.
3.  **Harden:** Add missing RLS policies and Audit triggers for all billing and operational tables.
4.  **Sync:** Update `docs/04 - sql.ddl` to reflect the actual production schema.
