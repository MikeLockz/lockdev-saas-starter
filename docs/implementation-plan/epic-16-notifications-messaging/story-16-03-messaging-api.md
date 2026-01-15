# Story 16.3: Messaging API
**User Story:** As a User, I want to send secure messages to my care team.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 5.1 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Messaging")

## Technical Specification
**Goal:** Implement threaded messaging system.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/messages.py` (NEW)
    - `MessageCreate` (body)
    - `MessageRead` (id, sender, body, created_at)
    - `ThreadCreate` (participant_ids, subject, patient_id?, initial_message)
    - `ThreadRead` (id, subject, participants, last_message, unread_count)
    - `ThreadListItem` (preview for inbox)

2.  **API Router:** `backend/src/api/messages.py` (NEW)
    - `GET /api/v1/organizations/{org_id}/messages`
      - List threads for current user (inbox)
      - Sort by last activity
      - Include unread indicator
    - `POST /api/v1/organizations/{org_id}/messages`
      - Create new thread with initial message
    - `GET /api/v1/organizations/{org_id}/messages/{thread_id}`
      - Get thread with all messages
      - Mark as read for current user
    - `POST /api/v1/organizations/{org_id}/messages/{thread_id}`
      - Send message to existing thread
      - Create notification for other participants

3.  **Business Logic:**
    - Only thread participants can view/send
    - Patient context optional (for care coordination)
    - Audit log message access (HIPAA)

## Acceptance Criteria
- [x] `GET /messages` returns user's threads.
- [x] `POST /messages` creates new thread.
- [x] `GET /messages/{id}` returns messages.
- [x] `POST /messages/{id}` adds message to thread.
- [x] Non-participants get 403.
- [x] Notifications sent to participants.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_messages.py`

**Manual Verification:**
- Create thread between two users.
- Send messages back and forth.
