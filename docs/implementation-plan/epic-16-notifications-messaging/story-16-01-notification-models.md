# Story 16.1: Notification & Messaging Models
**User Story:** As a Developer, I want notification and messaging models for the communication system.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 5.1 from `docs/10 - application implementation plan.md`
- **DDL Ref:** `docs/04 - sql.ddl` (notifications, message_threads, message_participants, messages)

## Technical Specification
**Goal:** Create models for notifications and threaded messaging.

**Changes Required:**

1.  **Migration:** `backend/migrations/versions/xxx_notifications.py`
    - Create `notifications` table:
      - `id` (UUID, PK)
      - `user_id` (FK to users)
      - `type` (String: APPOINTMENT, MESSAGE, SYSTEM, BILLING)
      - `title` (String)
      - `body` (Text)
      - `data_json` (JSONB, additional context)
      - `is_read` (Boolean, default False)
      - `read_at` (DateTime)
      - `created_at`

2.  **Migration:** `backend/migrations/versions/xxx_messaging.py`
    - Create `message_threads` table:
      - `id` (UUID, PK)
      - `organization_id` (FK)
      - `subject` (String)
      - `patient_id` (FK, optional - for patient context)
      - `created_at`, `updated_at`
    - Create `message_participants` table:
      - `thread_id` (FK, PK)
      - `user_id` (FK, PK)
      - `last_read_at` (DateTime)
    - Create `messages` table:
      - `id` (UUID, PK)
      - `thread_id` (FK)
      - `sender_id` (FK to users)
      - `body` (Text)
      - `created_at`

3.  **Models:** `backend/src/models/communications.py` (NEW)
    - `Notification`, `MessageThread`, `MessageParticipant`, `Message`

4.  **Indexes:**
    - `notifications`: (user_id, is_read), created_at
    - `messages`: thread_id, created_at

## Acceptance Criteria
- [x] All communication models created.
- [x] Appropriate indexes for performance.
- [x] Relationships properly defined.
- [x] Models exported in `__init__.py`.

## Verification Plan
**Automated Tests:**
- `alembic upgrade head` runs without errors

**Manual Verification:**
- Connect to DB, verify table structures.
