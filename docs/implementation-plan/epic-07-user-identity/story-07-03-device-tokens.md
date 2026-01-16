# Story 7.3: Device Tokens & Communication Preferences
**User Story:** As a User, I want to register my device for push notifications and manage my communication preferences, so that I receive relevant alerts.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 1.2 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Users & Authentication")
- **DDL Ref:** `docs/04 - sql.ddl` (user_devices table)

## Technical Specification
**Goal:** Implement FCM device token management and TCPA consent preferences.

**Changes Required:**

1.  **Migration:** `backend/migrations/versions/xxx_user_devices.py`
    - Create `user_devices` table:
      - `id` (UUID, PK)
      - `user_id` (FK to users)
      - `fcm_token` (String, unique per user)
      - `device_name` (String, e.g., "iPhone 15 Pro")
      - `platform` (String: "ios", "android", "web")
      - `created_at`, `updated_at`
    - Unique constraint on `(user_id, fcm_token)`

2.  **Model:** `backend/src/models/devices.py`
    - `UserDevice` SQLAlchemy model

3.  **Endpoints:** `backend/src/api/users.py`
    - `POST /api/v1/users/device-token`
      - Register FCM token for current user
      - Update if token already exists (upsert)
    - `DELETE /api/v1/users/device-token`
      - Remove device token (on logout)
      - Request body: `{ "fcm_token": "..." }`
    - `PATCH /api/v1/users/me/communication-preferences`
      - Update `transactional_consent`, `marketing_consent`
      - Audit log the change

4.  **Schemas:** `backend/src/schemas/users.py`
    - `DeviceTokenRequest` (fcm_token, device_name, platform)
    - `CommunicationPreferencesUpdate` (transactional_consent, marketing_consent)

## Acceptance Criteria
- [x] `POST /device-token` registers new device.
- [x] `POST /device-token` with existing token updates device info.
- [x] `DELETE /device-token` removes the device.
- [x] `PATCH /communication-preferences` updates consent flags.
- [x] User can have multiple devices registered.
- [x] Audit log captures preference changes.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_devices.py::test_register_device`
- `pytest tests/api/test_devices.py::test_remove_device`
- `pytest tests/api/test_users.py::test_update_communication_preferences`

**Manual Verification:**
- Register device, verify in database.
- Update preferences, verify in profile response.
