# Story 2.4: Domain Models (Users, Profiles, Tenants)
**User Story:** As a System Architect, I want the core entity models defined, so that we can support multi-tenancy and role separation.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 2.4 from `docs/03`
- **Schema:** `docs/04 - sql.ddl` (Reference)

## Technical Specification
**Goal:** Define SQLAlchemy models.

**Changes Required:**
1.  **File:** `backend/src/models/` (multiple files)
    - **Base:** `UUID` primary keys (ULID implementation).
    - **Tenancy:** `Organization` model.
    - **Identity:** `User` (email, MFA flags).
    - **Roles:**
        - `Provider` (NPI, licenses).
        - `Staff` (Job title).
        - `Patient` (MRN, DOB).
        - `Proxy` (Relationship type).
    - **Associations:**
        - `OrganizationMember` (User <-> Org).
        - `PatientProxyAssignment` (Patient <-> Proxy).
    - **Audit:** `AuditLog` model (Immutable).

## Acceptance Criteria
- [ ] All models defined with correct relationships.
- [ ] Soft delete (`deleted_at`) on clinical models.
- [ ] Migration generated successfully.

## Verification Plan
**Automated Tests:**
- Test creating a User and associated Patient profile.
- Test soft delete behavior (query filters out deleted).
