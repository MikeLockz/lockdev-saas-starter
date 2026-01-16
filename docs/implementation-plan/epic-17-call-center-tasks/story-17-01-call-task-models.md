# Story 17.1: Call & Task Models
**User Story:** As a Developer, I want call and task models for operational tracking.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 5.2 from `docs/10 - application implementation plan.md`
- **DDL Ref:** `docs/04 - sql.ddl` (Lines 362-400: `calls`, `tasks`)

## Technical Specification
**Goal:** Create models for call logging and task management.

**Changes Required:**

1.  **Migration:** `backend/migrations/versions/xxx_calls.py`
    - Create `calls` table:
      - `id` (UUID, PK)
      - `organization_id` (FK)
      - `patient_id` (FK, optional)
      - `agent_id` (FK to users)
      - `direction` (String: INBOUND, OUTBOUND)
      - `status` (String: QUEUED, IN_PROGRESS, COMPLETED, MISSED)
      - `phone_number` (String)
      - `started_at`, `ended_at`
      - `duration_seconds` (Integer)
      - `notes` (Text)
      - `outcome` (String: RESOLVED, CALLBACK_SCHEDULED, TRANSFERRED, VOICEMAIL)
      - `created_at`

2.  **Migration:** `backend/migrations/versions/xxx_tasks.py`
    - Create `tasks` table:
      - `id` (UUID, PK)
      - `organization_id` (FK)
      - `patient_id` (FK, optional)
      - `assignee_id` (FK to users)
      - `created_by_id` (FK to users)
      - `title` (String)
      - `description` (Text)
      - `status` (String: TODO, IN_PROGRESS, DONE, CANCELLED)
      - `priority` (String: LOW, MEDIUM, HIGH, URGENT)
      - `due_date` (Date)
      - `completed_at` (DateTime)
      - `created_at`, `updated_at`

3.  **Models:** `backend/src/models/operations.py` (NEW)
    - `Call`, `Task` SQLAlchemy models

4.  **Indexes:**
    - `calls`: (organization_id, status), agent_id
    - `tasks`: (assignee_id, status), due_date

## Acceptance Criteria
- [x] Call model has all fields.
- [x] Task model with priority and status.
- [x] Indexes created for queries.
- [x] Models exported in `__init__.py`.

## Verification Plan
**Automated Tests:**
- `alembic upgrade head` runs without errors

**Manual Verification:**
- Verify table structures in database.
