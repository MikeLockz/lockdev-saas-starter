# Critical Logic & Security Requirements Prompt

**Role:** You are a Principal Backend Architect and Security Specialist with deep expertise in HIPAA-compliant systems, PostgreSQL, and Python/FastAPI.

**Task:** Generate precise pseudo-code, state machines, and logic specifications for the high-risk "Critical Path" features of the Lockdev SaaS Platform.

**Context:**
We are building a HIPAA-compliant healthcare platform. Ambiguity in these specific areas leads to security vulnerabilities, data leaks, or patient safety risks. We need "Code-Ready" specifications that developers can implement immediately.

**Inputs:**
- `docs/03 - Implementation.md` (Architecture & RLS patterns)
- `docs/04 - sql.ddl` (Data Model)
- `docs/05 - API Reference.md` (API Contracts)

**Output Requirement:**
Generate a markdown file named `docs/09d - Critical Logic Specs.md` containing:

## 1. Safe Contact Protocol (Patient Safety)
**Goal:** Prevent accidental disclosure of PHI (e.g., domestic violence situations).
**Logic:**
- We distinguish between **Generic Messages** ("You have a new secure message.") and **Specific Messages** ("Your appointment with Dr. X is on Tuesday.").
- **Constraint:** NEVER send Specific Messages to a channel unless `is_safe_for_voicemail = true` (even for SMS).
- **Deliverables:**
    1.  **Notification Router Logic:** A Python function spec `async def route_notification(patient_id, priority, content_template, context)`.
        -   *Logic:* Iterate through `ContactMethod`s.
        -   *Safety Check:* If `!is_safe_for_voicemail`, downgrade content to "Generic".
        -   *Fallback:* Mobile App Push -> SMS (if safe) -> Email (if safe) -> Snail Mail (Last resort).
    2.  **Emergency Override:** Define logic for `priority="EMERGENCY"` where safety checks are bypassed (e.g., "ED Follow-up required immediately").
    3.  **Unit Test Matrix:** Table of inputs (Safety Flags + Message Priority) -> Expected Output (Channel + Content Type).

## 2. Multi-Factor Authentication (MFA) & Enforcement
**Goal:** Enforce 2FA for all Staff/Providers.
**Deliverables:**
    1.  **Setup Workflow:** Pseudo-code for `setup_mfa(user)` using `pyotp`.
        -   Generate Secret -> Store in DB (Encrypted) -> Return `otpauth` URL.
    2.  **Enforcement Middleware:** Pseudo-code for `MFAEnforcementMiddleware`.
        -   *Check:* Decode JWT. Look for custom claim `amr` (Authentication Methods References) or `mfa_verified=true`.
        -   *Block:* If user is `STAFF` and token lacks MFA claim, return 403 `MFA_REQUIRED`.
        -   *Exception:* Allow access to `/mfa/*` and `/auth/*` endpoints to permit setup.

## 3. Row Level Security (RLS) & Session Safety
**Goal:** Enforce multi-tenancy at the Database level to prevent data leaks.
**Context:** We use `asyncpg` with connection pooling.
**Deliverables:**
    1.  **SQL Policies:** Exact `CREATE POLICY` statements for `patients` and `appointments`.
        -   Policy: `tenant_id = current_setting('app.current_tenant_id', true)::uuid`.
    2.  **Session Context Manager (Python):**
        -   Refine the **Session Variable Safety Pattern** from `docs/03 - Implementation.md`.
        -   Show exactly how to use `sqlalchemy.event` to:
            1.  `SET LOCAL app.current_tenant_id` on transaction start.
            2.  `DISCARD ALL` on connection check-in (Critical for pool safety).

## 4. Audit Logging Strategy (Read vs. Write)
**Goal:** "If it happened, it's logged."
**Deliverables:**
    1.  **Write Auditing (DB Triggers):**
        -   PL/pgSQL Trigger Function `log_data_change()` that captures `OLD` vs `NEW` values.
        -   Must handle the `app.current_user_id` set by the application.
    2.  **Read Auditing (Middleware):**
        -   DB Triggers cannot easily capture `SELECT` queries without massive overhead.
        -   Design a `ReadAuditMiddleware` for FastAPI.
        -   *Logic:* Intercept `GET` requests to PHI endpoints -> Log `(actor_id, resource_path, query_params)` to `audit_logs`.

## 5. Stripe Subscription State Machine
**Goal:** Manage access based on payment status.
**Deliverables:**
    1.  **State Machine:** Diagram/Table handling `invoice.payment_succeeded`, `invoice.payment_failed`, `customer.subscription.deleted`.
    2.  **The "Grace Period" Logic:**
        -   If payment fails, set status to `PAST_DUE` (allow access for 7 days).
        -   If unpaid after 7 days, set `INACTIVE` (block access).
    3.  **Webhook Handler:** Pseudo-code for `handle_webhook(event)` ensuring **Idempotency** (checking if event ID was already processed).

## 6. Appointment Concurrency (Race Conditions)
**Goal:** Prevent double-booking slots.
**Deliverables:**
    1.  **Locking Strategy:**
        -   Option A: `SELECT ... FOR UPDATE` on the Provider's Schedule row.
        -   Option B: Postgres Advisory Locks using `pg_advisory_xact_lock(provider_id_hash, time_slot_hash)`.
    2.  **Implementation:** Pseudo-code for `book_appointment` using the chosen locking strategy inside a transaction.