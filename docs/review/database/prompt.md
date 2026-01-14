# Database Code Review Prompt

## Objective

You are conducting a comprehensive review of the database-related code in the Lockdev SaaS Starter project. Your goal is to verify adherence to the technical requirements, architectural principles, and implementation plans defined in the project documentation.

## Context Documents

Before beginning your review, you MUST read and understand the following documents:

1. **Technical Stack & Principles:** `/docs/tech-stack/00 - Overview.md`
   - Technology choices (PostgreSQL, SQLAlchemy, Alembic)
   - HIPAA compliance requirements
   - Data integrity standards (ULID primary keys, soft deletes)
   - Security and audit requirements

2. **Implementation Plans:** `/docs/implementation-plan/`
   - **Global Instructions:** `AA - Global Instructions.md` - Code style, safety protocols
   - **Master Orchestrator:** `00 - Master Orchestrator.md` - Overall project progress
   - **Epic 2: Backend Core** - Database foundation stories
   - **Epic 10: Patient Management** - Patient entity implementation
   - **Epic 11: Providers & Care Teams** - Provider and care team relationships
   - **Epic 14: Proxies** - Proxy patient access management
   - **Epic 15 & 22: Billing** - Billing infrastructure and complete billing
   - **Epic 18: Support & Compliance** - Audit logs and consent tracking
   - **Epic 20: Timezone Support** - Timezone handling in database

3. **Data Model Architecture:** `/docs/tech-stack/00 - Overview.md` (lines 92-159)
   - User actors & personas
   - Core entities and role entities
   - Association tables
   - Functional requirements (FR-01 through FR-07)

## Scope of Review

Your review should cover the following areas:

### 1. Database Configuration (`apps/backend/src/database.py`)

**Check for:**
- ✅ Async PostgreSQL engine with proper connection pooling
- ✅ RLS (Row-Level Security) implementation via `after_begin` event listener
- ✅ Session variables set correctly: `app.current_user_id`, `app.current_tenant_id`
- ✅ Connection pool cleanup via `checkin` listener with `DISCARD ALL`
- ✅ Proper session management with AsyncSessionLocal
- ✅ Error handling and connection resilience

**Questions to Answer:**
- Are RLS session variables being set on every database connection?
- Is the connection pool properly configured to prevent leakage?
- Does the configuration support multi-tenancy isolation?

### 2. SQLAlchemy Models (`apps/backend/src/schemas/*.py`)

**Core Model Requirements:**

#### **Mixins (`mixins.py`)**
- ✅ **UUIDMixin:** Uses ULID-to-UUID conversion for primary keys
- ✅ **TimestampMixin:** `created_at` and `updated_at` with server defaults
- ✅ **SoftDeleteMixin:** `deleted_at` timestamp for soft deletes

#### **User & Identity Models (`users.py`)**
- ✅ Email as unique identifier
- ✅ Password hashing (never plaintext)
- ✅ MFA support fields (`mfa_enabled`, `mfa_secret`)
- ✅ Timezone field (optional override per FR-07)
- ✅ `is_super_admin` flag for platform owners
- ✅ Relationships to Provider, Staff, Patient, Proxy profiles (1:1 optional)

#### **Organization Models (`organizations.py`)**
- ✅ Tenant isolation with `organization_id`
- ✅ Stripe integration fields (`stripe_customer_id`, `subscription_status`)
- ✅ JSONB settings field for flexible configuration
- ✅ Default timezone field (IANA format per FR-07)
- ✅ Member count and patient count tracking
- ✅ **OrganizationMembership** association table with roles (PROVIDER, STAFF, ADMIN)
- ✅ **OrganizationPatient** association table with status tracking

#### **Profile Models (`profiles.py`)**
- ✅ **Provider:** NPI, DEA, license fields, `state_licenses` JSONB array
- ✅ **Staff:** Employee ID, job title, department, active status
- ✅ **Patient:** MRN, DOB, legal sex, Stripe customer fields, billing manager assignment
- ✅ **Proxy:** Relationship type to patient

#### **Care & Assignments (`care_teams.py`, `assignments.py`)**
- ✅ **CareTeamAssignment:** Provider-to-patient linking with role hierarchy (PRIMARY, SPECIALIST, CONSULTANT)
- ✅ Unique constraint: one PRIMARY provider per patient
- ✅ **PatientProxyAssignment:** Granular permissions (can_view_profile, can_view_appointments, can_schedule_appointments, can_view_clinical_notes, can_view_billing, can_message_providers)
- ✅ Time-based access control (granted_at, expires_at, revoked_at)

#### **Clinical & Operational Models**
- ✅ **Appointments (`appointments.py`):** Status workflow, provider/patient/organization linkage
- ✅ **Documents (`documents.py`):** S3 integration, patient/organization association, status tracking
- ✅ **ContactMethods (`contacts.py`):** HIPAA-critical `is_safe_for_voicemail` flag
- ✅ **Calls & Tasks (`operations.py`):** Call tracking, task assignment with priorities

#### **Communications (`communications.py`)**
- ✅ **Notifications:** Type-based routing (APPOINTMENT, MESSAGE, SYSTEM, BILLING)
- ✅ **MessageThreads, MessageParticipants, Messages:** Thread-based messaging with read tracking

#### **Billing (`billing.py`)**
- ✅ **BillingTransaction:** Polymorphic owner (PATIENT or ORGANIZATION), Stripe integration
- ✅ Status values: SUCCEEDED, FAILED, REFUNDED, PENDING, CANCELLED
- ✅ Proxy management tracking (`managed_by_proxy_id`)
- ✅ **SubscriptionOverride:** Manual billing adjustments (FREE, TRIAL_EXTENSION, DISCOUNT)

#### **Audit & Compliance (`audit.py`, `consent.py`)**
- ✅ **AuditLog:** Immutable action tracking (READ, CREATE, UPDATE, DELETE)
- ✅ IP address storage (PostgreSQL INET type)
- ✅ Impersonation tracking (`impersonator_id`)
- ✅ **ConsentDocument:** Versioned TOS/HIPAA/Privacy policies
- ✅ **UserConsent:** Signed consent records with IP tracking

#### **Support (`support.py`)**
- ✅ **SupportTicket:** Category, priority, status workflow
- ✅ **SupportMessage:** Internal vs external message distinction

#### **Sessions & Devices (`sessions.py`, `devices.py`)**
- ✅ **UserSession:** Session timeout for HIPAA compliance, revocation support
- ✅ **UserDevice:** FCM tokens for push notifications

### 3. Database Migrations (`apps/backend/migrations/versions/*.py`)

**Check for:**
- ✅ Proper migration naming convention
- ✅ Alembic upgrade/downgrade functions
- ✅ Index creation for frequently queried fields
- ✅ Unique constraints matching business rules
- ✅ Check constraints for data validation
- ✅ Foreign key relationships with proper CASCADE rules
- ✅ RLS policy creation and enablement
- ✅ Audit trigger installation
- ✅ Migration reversibility (downgrade logic)

**Questions to Answer:**
- Can migrations be safely rolled back?
- Are all necessary indexes created for performance?
- Do RLS policies correctly enforce tenant isolation?

### 4. HIPAA Compliance

**Critical Requirements:**
- ✅ **Soft Deletes:** Clinical data NEVER hard deleted (FR-03 assumption #3)
- ✅ **Audit Logs:** All sensitive actions tracked with actor, timestamp, IP address
- ✅ **RLS Policies:** Data segregated by tenant and user context
- ✅ **Contact Safety:** `is_safe_for_voicemail` flag respected
- ✅ **Session Timeout:** User sessions expire appropriately
- ✅ **Consent Tracking:** TOS/HIPAA consent versioned and signed

**Questions to Answer:**
- Are all PHI-containing tables protected by RLS?
- Is there an audit trail for all data access and modifications?
- Can we demonstrate HIPAA compliance for data deletion (soft delete)?

### 5. Data Integrity

**Check for:**
- ✅ **ULID Primary Keys:** All tables use ULID-to-UUID conversion (not sequential integers)
- ✅ **Timestamps:** `created_at`, `updated_at` with server defaults
- ✅ **Soft Deletes:** `deleted_at` on all clinical/patient-related tables
- ✅ **Referential Integrity:** Foreign keys defined correctly
- ✅ **Unique Constraints:** Business rules enforced at DB level
- ✅ **Check Constraints:** Data validation (e.g., percentage ranges, enum values)
- ✅ **NOT NULL Constraints:** Required fields enforced

**Questions to Answer:**
- Are there any opportunities for data corruption or orphaned records?
- Are all business rules enforced at the database level?
- Is there proper validation to prevent invalid data states?

### 6. Multi-Tenancy & RLS

**Check for:**
- ✅ `organization_id` on all tenant-scoped tables
- ✅ RLS policies enabled on tenant-scoped tables
- ✅ Context variables (`app.current_tenant_id`, `app.current_user_id`) set before queries
- ✅ Super admin bypass logic (if applicable)
- ✅ Cross-organization access controls (e.g., providers working at multiple clinics)

**Questions to Answer:**
- Can a user from Organization A access Organization B's data?
- Are RLS policies correctly enforcing tenant isolation?
- Do providers with multi-organization access see the correct data?

### 7. Relationships & Associations

**Verify Correctness of:**
- ✅ **User → Role Profiles:** 1:1 optional relationships (can be Provider OR Staff OR Patient OR Proxy)
- ✅ **User ↔ Organization:** Many-to-many via OrganizationMembership with roles
- ✅ **Patient ↔ Organization:** Many-to-many via OrganizationPatient with enrollment status
- ✅ **Patient ↔ Proxy:** Many-to-many via PatientProxyAssignment with granular permissions
- ✅ **Provider ↔ Patient:** Many-to-many via CareTeamAssignment with role hierarchy
- ✅ **Cascade Deletes:** Orphaned records prevented via proper cascade rules

**Questions to Answer:**
- Can relationships be created that violate business rules?
- Are there any missing foreign key constraints?
- Do cascade delete rules align with business requirements?

### 8. Performance Considerations

**Check for:**
- ✅ **Indexes on Foreign Keys:** All FK columns indexed
- ✅ **Composite Indexes:** Multi-column queries optimized
- ✅ **JSONB Indexes:** GIN indexes on JSONB columns where needed
- ✅ **Query Patterns:** N+1 query prevention via relationships and eager loading
- ✅ **Connection Pooling:** Properly configured pool size and timeouts

**Questions to Answer:**
- Are there missing indexes that could cause performance issues?
- Is the connection pool sized appropriately for the expected load?
- Are JSONB queries optimized with appropriate indexes?

### 9. Timezone Handling (FR-07)

**Check for:**
- ✅ All datetime fields use timezone-aware types (`DateTime(timezone=True)`)
- ✅ Organization has `timezone` field (IANA format, e.g., "America/New_York")
- ✅ User has optional `timezone` override (null = use organization default)
- ✅ All datetimes stored as UTC in database
- ✅ Timezone conversion handled at application layer (not in database)

**Questions to Answer:**
- Are all datetime fields timezone-aware?
- Is there a clear strategy for timezone conversion?
- Can we correctly display times in user/organization local time?

### 10. Subscription & Billing (FR-06)

**Check for:**
- ✅ **Dual-Sided Model:** Both Organization and Patient have `stripe_customer_id` and `subscription_status`
- ✅ **Billing Transactions:** Polymorphic owner support (PATIENT or ORGANIZATION)
- ✅ **Proxy Management:** `managed_by_proxy_id` tracked for proxy-initiated payments
- ✅ **Subscription Overrides:** Manual adjustments (FREE, TRIAL_EXTENSION, DISCOUNT)
- ✅ **Billing Manager:** Patient `billing_manager_id` links to Provider

**Questions to Answer:**
- Can both organizations and patients be billed independently?
- Are proxy-initiated payments properly tracked?
- Can billing be overridden for special cases (trials, discounts)?

## Review Process

### Step 1: Read Documentation
- Read all context documents listed above
- Understand the technical requirements and architectural principles
- Review the implementation plans for database-related epics

### Step 2: Code Inspection
- Review database configuration in `apps/backend/src/database.py`
- Review all SQLAlchemy models in `apps/backend/src/schemas/*.py`
- Review migrations in `apps/backend/migrations/versions/*.py`

### Step 3: Checklist Validation
- Go through each checklist item in sections 1-10 above
- Mark items as ✅ Pass, ⚠️ Warning, or ❌ Fail
- Document specific findings for warnings and failures

### Step 4: Answer Key Questions
- Answer all "Questions to Answer" from sections 1-10
- Provide specific file paths and line numbers for issues

## Output Format

Your review should be structured as follows:

### Executive Summary
- Overall assessment (Pass / Pass with Warnings / Fail)
- Critical issues count
- Warning issues count
- Key strengths observed

### Detailed Findings

For each section (1-10), provide:

**Section X: [Section Name]**
- **Status:** ✅ Pass / ⚠️ Pass with Warnings / ❌ Fail
- **Checklist Results:** List items that failed or have warnings
- **Key Question Answers:** Answer the questions with specific details
- **Issues Found:**
  - **Critical:** [Description, file:line, impact, recommendation]
  - **Warning:** [Description, file:line, impact, recommendation]
  - **Info:** [Observation, potential improvement]

### Compliance Assessment

**HIPAA Compliance:**
- Audit logging: ✅/⚠️/❌
- Data segregation (RLS): ✅/⚠️/❌
- Soft deletes: ✅/⚠️/❌
- Consent tracking: ✅/⚠️/❌
- Session security: ✅/⚠️/❌

**Data Integrity:**
- Primary keys (ULID): ✅/⚠️/❌
- Referential integrity: ✅/⚠️/❌
- Soft deletes: ✅/⚠️/❌
- Constraints: ✅/⚠️/❌

**Multi-Tenancy:**
- Tenant isolation: ✅/⚠️/❌
- RLS enforcement: ✅/⚠️/❌
- Cross-org access: ✅/⚠️/❌

### Recommendations

1. **Critical (Must Fix):** [List critical issues requiring immediate attention]
2. **High Priority (Should Fix):** [List important issues to address soon]
3. **Medium Priority (Nice to Have):** [List improvements for consideration]
4. **Performance Optimizations:** [List potential performance improvements]

### Positive Observations

- [List architectural strengths and good practices observed]

## Success Criteria

The database code review is considered successful if:

1. **No Critical Issues:** All critical issues (security, HIPAA, data integrity) are addressed
2. **HIPAA Compliance:** All HIPAA requirements are met (audit, RLS, soft deletes, consent)
3. **Multi-Tenancy:** Tenant isolation is properly enforced via RLS
4. **Data Integrity:** ULID primary keys, soft deletes, and constraints are correctly implemented
5. **Performance:** Appropriate indexes exist for common query patterns
6. **Documentation Alignment:** Implementation matches the requirements in `/docs/tech-stack/00 - Overview.md` and `/docs/implementation-plan/`

## Additional Notes

- **Be Thorough:** This is a healthcare SaaS platform - data integrity and security are paramount
- **Be Specific:** Always cite file paths and line numbers for findings
- **Be Constructive:** Provide actionable recommendations, not just criticism
- **Be Compliant:** Prioritize HIPAA and security requirements above all else
- **Be Architectural:** Consider scalability, maintainability, and extensibility

---

**Ready to begin your review?** Start by reading the context documents, then systematically review each section above. Good luck!
