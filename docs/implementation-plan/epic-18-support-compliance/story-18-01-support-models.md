# Story 18.1: Support Ticket Models
**User Story:** As a Developer, I want support ticket models for help desk functionality.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 5.3 from `docs/10 - application implementation plan.md`
- **DDL Ref:** `docs/04 - sql.ddl` (Lines 413-439: `support_tickets`, `support_messages`)

## Technical Specification
**Goal:** Create models for support ticket system.

**Changes Required:**

1.  **Migration:** `backend/migrations/versions/xxx_support.py`
    - Create `support_tickets` table:
      - `id` (UUID, PK)
      - `user_id` (FK to users)
      - `organization_id` (FK, optional)
      - `subject` (String)
      - `category` (String: TECHNICAL, BILLING, ACCOUNT, OTHER)
      - `priority` (String: LOW, MEDIUM, HIGH)
      - `status` (String: OPEN, IN_PROGRESS, RESOLVED, CLOSED)
      - `assigned_to_id` (FK to users, support agent)
      - `created_at`, `updated_at`, `resolved_at`
    - Create `support_messages` table:
      - `id` (UUID, PK)
      - `ticket_id` (FK)
      - `sender_id` (FK to users)
      - `body` (Text)
      - `is_internal` (Boolean, staff-only note)
      - `created_at`

2.  **Models:** `backend/src/models/support.py` (NEW)
    - `SupportTicket`, `SupportMessage` models

3.  **Indexes:**
    - `support_tickets`: (status, assigned_to_id), user_id

## Acceptance Criteria
- [x] Support ticket model complete.
- [x] Support message with internal flag.
- [x] Indexes for agent queue.
- [x] Models exported in `__init__.py`.

## Verification Plan
**Automated Tests:**
- `alembic upgrade head` runs without errors

**Manual Verification:**
- Verify tables in database.
