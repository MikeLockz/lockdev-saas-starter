# Story 7.1: User Profile & Session Endpoints
**User Story:** As a User, I want to manage my profile and view active sessions, so that I have control over my account security.

## Status
- [x] **Complete** (2026-01-02)

## Context
- **Roadmap Ref:** Step 1.2 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Users & Authentication")

## Technical Specification
**Goal:** Implement user profile CRUD and session management endpoints.

**Changes Required:**

1.  **Migration:** `backend/migrations/versions/xxx_user_sessions.py`
    - Create `user_sessions` table:
      - `id` (UUID, PK)
      - `user_id` (FK to users)
      - `device_info` (JSONB: user_agent, ip, etc.)
      - `firebase_uid` (String, for token tracking)
      - `created_at`, `last_active_at`, `expires_at` (timestamps)
      - `is_revoked` (Boolean)

2.  **Model:** `backend/src/models/sessions.py`
    - `UserSession` SQLAlchemy model

3.  **Endpoints:** `backend/src/api/users.py`
    - `GET /api/v1/users/me/sessions` - List active sessions
    - `DELETE /api/v1/users/me/sessions/{session_id}` - Revoke a session
    - `PATCH /api/v1/users/me` - Update display_name, communication preferences
    - `POST /api/v1/users/me/export` - Trigger HIPAA data export (queue job)
    - `DELETE /api/v1/users/me` - Soft delete account

4.  **Schemas:** `backend/src/schemas/users.py`
    - `UserUpdate` (display_name, transactional_consent, marketing_consent)
    - `SessionRead` (id, device_info, created_at, last_active_at)

5.  **Middleware Update:** `backend/src/security/auth.py`
    - Create/update session record on token verification
    - Track `last_active_at`

## Acceptance Criteria
- [x] `GET /users/me/sessions` returns list of active sessions with device info.
- [x] `DELETE /users/me/sessions/{id}` marks session as revoked.
- [x] `PATCH /users/me` updates user profile fields.
- [x] `POST /users/me/export` queues a background job and returns 202.
- [x] `DELETE /users/me` sets `deleted_at` and returns 204.
- [x] All endpoints create audit log entries (via user_sessions audit trigger).

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_users.py::test_list_sessions`
- `pytest tests/api/test_users.py::test_revoke_session`
- `pytest tests/api/test_users.py::test_update_profile`
- `pytest tests/api/test_users.py::test_delete_account`

**Manual Verification:**
- Log in from two browsers, list sessions shows both.
- Revoke one session, that browser gets logged out.
