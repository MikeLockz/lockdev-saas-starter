# Story 16.2: Notification API
**User Story:** As a User, I want to view and manage my notifications.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 5.1 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Notifications")

## Technical Specification
**Goal:** Implement notification CRUD and bulk operations.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/notifications.py` (NEW)
    - `NotificationRead` (all fields)
    - `NotificationListResponse` (items, unread_count)

2.  **API Router:** `backend/src/api/notifications.py` (NEW)
    - `GET /api/v1/users/me/notifications`
      - List user's notifications (paginated)
      - Filter by is_read, type
      - Return unread_count in response
    - `GET /api/v1/users/me/notifications/unread-count`
      - Quick count for badge display
    - `PATCH /api/v1/users/me/notifications/{notification_id}`
      - Mark as read/unread
    - `POST /api/v1/users/me/notifications/mark-all-read`
      - Bulk mark all as read
    - `DELETE /api/v1/users/me/notifications/{notification_id}`
      - Dismiss notification

3.  **Service:** `backend/src/services/notifications.py` (NEW)
    - `create_notification(user_id, type, title, body, data)`
    - Called from other services (appointments, messages, etc.)

## Acceptance Criteria
- [x] `GET /notifications` returns paginated list.
- [x] Unread count accurate.
- [x] Mark as read updates is_read and read_at.
- [x] Mark-all-read bulk updates.
- [x] Delete removes notification.
- [x] Notifications created from system events.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_notifications.py`

**Manual Verification:**
- Create notification, verify in list.
- Mark as read, verify count updates.
