# Backend Implementation Specification

This document details the technical implementation for the API endpoints defined in `docs/05 - API Reference.md`, mapped to the schema in `docs/04 - sql.ddl`.

> [!IMPORTANT]
> **Tenancy Rule:** All queries accessing organization-scoped resources **MUST** include `WHERE organization_id = :org_id` to prevent data leaks.
> **Soft Delete Rule:** All queries for entities with `deleted_at` **MUST** include `AND deleted_at IS NULL` unless explicitly querying for deleted records (e.g. Audit Logs).
> **Audit Middleware:** A global middleware MUST intercept all requests hitting endpoints marked with 🔒 in the API Reference. It MUST asynchronously log the access to `audit_logs` without blocking the response. for `READ` operations, the resource ID should be extracted from the path.

---

## 1. Users & Authentication

### `GET /api/users/me`
**Summary**: Retrieve current user's profile, roles, and context.
**SQL**:
```sql
SELECT u.id, u.email, u.display_name, u.is_super_admin, u.mfa_enabled, 
       u.transactional_consent, u.marketing_consent, u.last_login_at, u.created_at,
       (SELECT json_agg(json_build_object('organization_id', om.organization_id, 'role', om.role, 'organization_name', o.name)) 
        FROM organization_memberships om 
        JOIN organizations o ON om.organization_id = o.id 
        WHERE om.user_id = u.id AND om.deleted_at IS NULL) as roles,
       (SELECT id FROM patients WHERE user_id = u.id AND deleted_at IS NULL) as patient_profile_id,
       (SELECT id FROM proxies WHERE user_id = u.id AND deleted_at IS NULL) as proxy_profile_id
FROM users u
WHERE u.id = :current_user_id AND u.deleted_at IS NULL;
```

### `PATCH /api/users/me`
**Summary**: Update user profile.
**SQL**:
```sql
UPDATE users SET display_name = :display_name, updated_at = NOW() WHERE id = :user_id RETURNING *;
```

### `POST /api/users/device-token`
**Summary**: Register FCM token.
**SQL**:
```sql
INSERT INTO user_devices (user_id, fcm_token, platform)
VALUES (:user_id, :token, :platform)
ON CONFLICT (user_id, fcm_token) DO UPDATE SET last_active_at = NOW();
```

### `DELETE /api/users/device-token`
**Summary**: Remove FCM token.
**SQL**:
```sql
DELETE FROM user_devices WHERE user_id = :user_id AND fcm_token = :token;
```

### `GET /api/users/me/communication-preferences`
**Summary**: Get consent status.
**SQL**:
```sql
SELECT transactional_consent, marketing_consent FROM users WHERE id = :user_id;
```

### `PATCH /api/users/me/communication-preferences`
**Summary**: Update consent.
**SQL**:
```sql
UPDATE users SET transactional_consent = :transactional, marketing_consent = :marketing, updated_at = NOW() 
WHERE id = :user_id 
RETURNING transactional_consent, marketing_consent;
```

---

## 2. User Sessions

### `GET /api/users/me/sessions`
**Logic**: Firebase Admin SDK `auth.listSessions(uid)`.

### `DELETE /api/users/me/sessions/{session_id}`
**Logic**: Firebase Admin SDK `auth.revokeRefreshTokens(uid)` (if global) or manage custom session mapping if implementing custom session tracking. *MVP assumes standard Firebase token revocation.*

### `DELETE /api/users/me`
**Summary**: Soft delete account.
**Logic**: Soft delete user + cascading soft delete memberships.
**SQL**:
```sql
BEGIN;
UPDATE users SET deleted_at = NOW() WHERE id = :user_id;
UPDATE organization_memberships SET deleted_at = NOW() WHERE user_id = :user_id;
UPDATE providers SET deleted_at = NOW() WHERE user_id = :user_id;
UPDATE staff SET deleted_at = NOW() WHERE user_id = :user_id;
-- Also delete patient/proxy profiles to prevent orphaned PHI access
UPDATE patients SET deleted_at = NOW() WHERE user_id = :user_id;
UPDATE proxies SET deleted_at = NOW() WHERE user_id = :user_id;
UPDATE user_devices SET fcm_token = 'DELETED_' || fcm_token WHERE user_id = :user_id; -- Invalidate tokens
COMMIT;
```

### `POST /api/users/me/export`
**Summary**: HIPAA Right of Access.
**Logic**: Trigger async job `ExportUserData(user_id)`.
**Audit**:
```sql
INSERT INTO audit_logs (actor_user_id, action_type, resource_type, resource_id) 
VALUES (:user_id, 'EXPORT', 'USER_DATA', :user_id);
```

---

## 3. Notifications

### `GET /api/users/me/notifications`
**SQL**:
```sql
SELECT * FROM notifications 
WHERE user_id = :user_id 
  AND (:filter_unread IS FALSE OR is_read = FALSE)
  AND (:type IS NULL OR type = :type)
ORDER BY created_at DESC 
LIMIT :limit OFFSET :offset;
```

### `PATCH /api/users/me/notifications/{id}`
**Summary**: Mark read.
**SQL**:
```sql
UPDATE notifications SET is_read = :is_read WHERE id = :id AND user_id = :user_id RETURNING *;
```

### `POST /api/users/me/notifications/mark-all-read`
**SQL**:
```sql
UPDATE notifications SET is_read = TRUE 
WHERE user_id = :user_id AND created_at < :before_timestamp;
```

### `DELETE /api/users/me/notifications/{id}`
**SQL**:
```sql
DELETE FROM notifications WHERE id = :id AND user_id = :user_id;
-- Note: If soft delete is preferred, use UPDATE notifications SET deleted_at = NOW()...
-- Current Schema supports soft delete.
UPDATE notifications SET deleted_at = NOW() WHERE id = :id AND user_id = :user_id;
```

---

## 4. MFA

### `POST /api/users/me/mfa/setup`
**Logic**: Generate TOTP Secret (pyotp), store in Redis (temp).
**Return**: `otpauth://` URL / QR Code.

### `POST /api/users/me/mfa/verify`
**Logic**: Validate code. If valid:
**SQL**:
```sql
UPDATE users SET mfa_enabled = TRUE, updated_at = NOW() WHERE id = :user_id;
```

### `POST /api/users/me/mfa/backup-codes`
**Logic**: Generate, Hash, Store.
**SQL**:
```sql
BEGIN;
DELETE FROM user_mfa_backup_codes WHERE user_id = :user_id;
INSERT INTO user_mfa_backup_codes (user_id, code_hash) VALUES (:user_id, :hash_1), ...;
COMMIT;
```

### `DELETE /api/users/me/mfa`
**Logic**: Disable MFA (Requires Admin/Provider check - some roles CANNOT disable).
**SQL**:
```sql
UPDATE users SET mfa_enabled = FALSE WHERE id = :user_id;
DELETE FROM user_mfa_backup_codes WHERE user_id = :user_id;
```

---

## 5. Organizations

### `GET /api/organizations`
**SQL**:
```sql
SELECT o.*, om.role 
FROM organizations o
JOIN organization_memberships om ON o.id = om.organization_id
WHERE om.user_id = :user_id AND o.deleted_at IS NULL AND om.deleted_at IS NULL;
```

### `POST /api/organizations`
**SQL**:
```sql
BEGIN;
INSERT INTO organizations (name, tax_id, settings_json) VALUES (...) RETURNING id;
INSERT INTO organization_memberships (organization_id, user_id, role) VALUES (:new_org_id, :user_id, 'ADMIN');
COMMIT;
```

### `GET /api/organizations/{org_id}`
**Auth**: Member Check.
**SQL**: `SELECT * FROM organizations WHERE id = :org_id;`

### `PATCH /api/organizations/{org_id}`
**Auth**: ADMIN only.
**SQL**: `UPDATE organizations SET name = :name, settings_json = :settings WHERE id = :org_id;`

### `DELETE /api/organizations/{org_id}`
**Auth**: ADMIN only.
**SQL**:
```sql
UPDATE organizations SET deleted_at = NOW() WHERE id = :org_id;
-- Memberships cascade via application logic or trigger, or remain active but pointing to deleted org (handled by join check).
```

---

## 6. Organization Members

### `GET /api/organizations/{org_id}/members`
**SQL**:
```sql
SELECT om.*, u.email, u.display_name, u.mfa_enabled
FROM organization_memberships om
JOIN users u ON om.user_id = u.id
WHERE om.organization_id = :org_id AND om.deleted_at IS NULL;
```

### `POST /api/organizations/{org_id}/members`
**Logic**: Explicit invite flow.
**SQL**:
```sql
INSERT INTO invitations (organization_id, email, role, token, expires_at, inviter_user_id)
VALUES (:org_id, :email, :role, :token, NOW() + INTERVAL '7 days', :user_id)
RETURNING id;
```
**Action**: Send Email with link.

### `PATCH /api/organizations/{org_id}/members/{member_id}`
**SQL**: `UPDATE organization_memberships SET role = :new_role WHERE id = :member_id AND organization_id = :org_id;`

### `DELETE /api/organizations/{org_id}/members/{member_id}`
**SQL**: `UPDATE organization_memberships SET deleted_at = NOW() WHERE id = :member_id AND organization_id = :org_id;`

---

## 7. Invitations

### `GET /api/organizations/{org_id}/invitations`
**SQL**: `SELECT * FROM invitations WHERE organization_id = :org_id AND status = 'PENDING';`

### `POST /api/invitations/{token}/accept`
**Logic**: Verify token, Match User.
**SQL**:
```sql
BEGIN;
UPDATE invitations SET status = 'ACCEPTED', updated_at = NOW() WHERE token = :token;
INSERT INTO organization_memberships (organization_id, user_id, role) 
  SELECT organization_id, :current_user_id, role FROM invitations WHERE token = :token;
COMMIT;
```

### `POST /api/invitations/{token}/decline`
**Logic**: Mark as DECLINED.
**SQL**:
```sql
UPDATE invitations SET status = 'DECLINED', updated_at = NOW() WHERE token = :token;
```

### `GET /api/invitations/{token}`
**Logic**: Retrieve public invitation info. Validates token format/expiry.
**SQL**:
```sql
SELECT i.role, i.email as invited_email, i.expires_at, i.created_at,
       o.id as organization_id, o.name as organization_name, o.settings_json->>'logo_url' as organization_logo_url,
       u.display_name as inviter_name, u.email as inviter_email
FROM invitations i
JOIN organizations o ON i.organization_id = o.id
LEFT JOIN users u ON i.inviter_user_id = u.id
WHERE i.token = :token AND i.status = 'PENDING' AND i.expires_at > NOW();
```

---

### `POST /api/organizations/{org_id}/invitations/{invitation_id}/resend`
**Logic**: Verify status is PENDING. Extend expiry.
**SQL**:
```sql
UPDATE invitations 
SET expires_at = NOW() + INTERVAL '7 days', resend_count = resend_count + 1, updated_at = NOW()
WHERE id = :invitation_id AND organization_id = :org_id AND status = 'PENDING'
RETURNING *;
```

### `DELETE /api/organizations/{org_id}/invitations/{invitation_id}`
**Summary**: Cancel invitation.
**SQL**:
```sql
UPDATE invitations SET status = 'CANCELLED', updated_at = NOW() 
WHERE id = :invitation_id AND organization_id = :org_id AND status = 'PENDING';
```

---

## 8. Patients

### `GET /api/organizations/{org_id}/patients`
**Performance**: Uses `idx_patients_names` / `idx_patients_mrn_trgm`.
**SQL**:
```sql
SELECT p.*, op.status, op.enrolled_at
FROM patients p
JOIN organization_patients op ON p.id = op.patient_id
WHERE op.organization_id = :org_id 
  AND (:search IS NULL OR (p.last_name ILIKE :search OR p.first_name ILIKE :search OR p.medical_record_number ILIKE :search))
  AND p.deleted_at IS NULL
LIMIT :limit OFFSET :offset;
```

### `GET /api/organizations/{org_id}/patients/{patient_id}`
**Audit**: `READ`.
**SQL**:
```sql
SELECT p.*, op.status, op.enrolled_at, op.discharged_at
FROM patients p
JOIN organization_patients op ON p.id = op.patient_id
WHERE p.id = :patient_id AND op.organization_id = :org_id;
```

### `POST /api/organizations/{org_id}/patients`
**Audit**: `CREATE`.
**SQL**:
```sql
BEGIN;
INSERT INTO patients (first_name, last_name, dob, medical_record_number) VALUES (...) RETURNING id;
INSERT INTO organization_patients (organization_id, patient_id) VALUES (:org_id, :new_id);
INSERT INTO contact_methods (patient_id, type, value, is_primary) VALUES (...);
COMMIT;
```

### `PATCH /api/organizations/{org_id}/patients/{patient_id}`
**Audit**: `UPDATE`.
**SQL**: `UPDATE patients SET first_name=:first, ... WHERE id=:id;`

### `DELETE /api/organizations/{org_id}/patients/{patient_id}`
**Audit**: `DELETE`.
**SQL**: `UPDATE patients SET deleted_at = NOW() WHERE id = :id;`

---

## 9. Contact Methods

### `GET /api/organizations/{org_id}/patients/{patient_id}/contact-methods`
**SQL**: `SELECT * FROM contact_methods WHERE patient_id = :patient_id;`

### `POST ...`
**SQL**: `INSERT INTO contact_methods (...) VALUES (...);`

### `PATCH ...`
**SQL**: `UPDATE contact_methods SET is_primary = :primary, is_safe_for_voicemail = :safe WHERE id = :id;`

### `DELETE ...`
**SQL**: `DELETE FROM contact_methods WHERE id = :id;`

---

## 10. Organization-Patient Relationships

### `GET .../enrollment`
**SQL**: `SELECT * FROM organization_patients WHERE organization_id = :org_id AND patient_id = :patient_id;`

### `PATCH .../enrollment`
**Summary**: Discharge patient.
**SQL**: `UPDATE organization_patients SET status = :status, discharged_at = (CASE WHEN :status='DISCHARGED' THEN NOW() ELSE NULL END) WHERE organization_id = :org_id AND patient_id = :patient_id;`

### `GET /api/patients/{patient_id}/organizations`
**SQL**:
```sql
SELECT o.id, o.name, op.status 
FROM organization_patients op
JOIN organizations o ON op.organization_id = o.id
WHERE op.patient_id = :patient_id;
```

---

## 11. Providers & Staff

### `GET /api/organizations/{org_id}/providers`
**SQL**:
```sql
SELECT p.*, u.display_name 
FROM providers p
JOIN users u ON p.user_id = u.id
JOIN organization_memberships om ON u.id = om.user_id
WHERE om.organization_id = :org_id AND om.role = 'PROVIDER' AND p.deleted_at IS NULL;
```

### `POST ...` (Create Provider Profile)
**SQL**: `INSERT INTO providers (user_id, npi_number, specialty) VALUES (...) RETURNING id;`

### `DELETE ...`
**SQL**: `UPDATE providers SET deleted_at = NOW() WHERE id = :id;`

---

### `GET /api/organizations/{org_id}/providers/{provider_id}`
**SQL**: `SELECT * FROM providers WHERE id = :provider_id AND deleted_at IS NULL;`

### `GET /api/organizations/{org_id}/providers/{provider_id}/availability`
**Logic**: 
1. Fetch provider's scheduled appointments for range.
2. Overlay on default operating hours (e.g. 9-5) in application code to find gaps.
**SQL**:
```sql
SELECT * FROM appointments 
WHERE provider_id = :provider_id 
  AND scheduled_at BETWEEN :start_date AND :end_date
  AND status NOT IN ('CANCELLED', 'NO_SHOW')
  AND deleted_at IS NULL;
```

### `GET /api/organizations/{org_id}/staff`
**SQL**:
```sql
SELECT s.*, u.display_name 
FROM staff s
JOIN users u ON s.user_id = u.id
JOIN organization_memberships om ON u.id = om.user_id
WHERE om.organization_id = :org_id AND om.role = 'STAFF' AND s.deleted_at IS NULL;
```

### `GET /api/organizations/{org_id}/staff/{staff_id}`
**SQL**: `SELECT * FROM staff WHERE id = :staff_id AND deleted_at IS NULL;`

### `POST /api/organizations/{org_id}/staff`
**SQL**: `INSERT INTO staff (user_id, employee_id, job_title) VALUES (...) RETURNING id;`

### `PATCH /api/organizations/{org_id}/staff/{staff_id}`
**SQL**: `UPDATE staff SET job_title = :title, updated_at = NOW() WHERE id = :id;`

### `DELETE /api/organizations/{org_id}/staff/{staff_id}`
**SQL**: `UPDATE staff SET deleted_at = NOW() WHERE id = :id;`

---

## 12. Care Team

### `GET .../care-team`
**SQL**:
```sql
SELECT cta.*, u.display_name as provider_name
FROM care_team_assignments cta
JOIN providers p ON cta.provider_id = p.id
JOIN users u ON p.user_id = u.id
WHERE cta.organization_id = :org_id AND cta.patient_id = :patient_id;
```

### `POST .../care-team`
**SQL**: `INSERT INTO care_team_assignments (organization_id, patient_id, provider_id, is_primary_provider) VALUES (...);`

### `DELETE .../care-team/{id}`
**SQL**: `DELETE FROM care_team_assignments WHERE id = :id;`

---

## 13. Proxies

### `GET /api/organizations/{org_id}/patients/{patient_id}/proxies`
**SQL**:
```sql
SELECT ppa.*, u.display_name as proxy_name, u.email as proxy_email
FROM patient_proxy_assignments ppa
JOIN proxies px ON ppa.proxy_id = px.id
JOIN users u ON px.user_id = u.id
WHERE ppa.patient_id = :patient_id AND ppa.deleted_at IS NULL;
```

### `POST .../proxies` (Assign Proxy)
**Audit**: `GRANT_ACCESS`
**SQL**: `INSERT INTO patient_proxy_assignments (proxy_id, patient_id, relationship_type, permissions...) VALUES (...);`

### `DELETE .../proxies/{id}`
**Audit**: `REVOKE_ACCESS`
**SQL**: `UPDATE patient_proxy_assignments SET deleted_at = NOW() WHERE id = :id;`

---

## 14. Appointments
 
### `GET /api/organizations/{org_id}/appointments`
**Performance**: Range query for index usage. Limit/Offset for pagination.
**SQL**:
```sql
SELECT a.*, p.first_name, p.last_name, u.display_name as provider_name
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN providers pr ON a.provider_id = pr.id
JOIN users u ON pr.user_id = u.id
WHERE a.organization_id = :org_id 
  AND (:start_date IS NULL OR a.scheduled_at >= :start_date)
  AND (:end_date IS NULL OR a.scheduled_at < :end_date)
  AND a.deleted_at IS NULL
ORDER BY a.scheduled_at ASC
LIMIT :limit OFFSET :offset;
```
 
### `GET .../appointments/{appointment_id}`
**Audit**: `READ`
**SQL**:
```sql
SELECT a.*, p.first_name, p.last_name, u.display_name as provider_name
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN users u ON (SELECT user_id FROM providers WHERE id = a.provider_id) = u.id
WHERE a.id = :appointment_id AND a.organization_id = :org_id;
```

### `POST ...`
**Audit**: `CREATE`
**SQL**: `INSERT INTO appointments (...) VALUES (...) RETURNING id;`
 
### `PATCH .../{id}`
**Audit**: `UPDATE`
**SQL**: `UPDATE appointments SET status = :status, updated_at = NOW() WHERE id = :id AND organization_id = :org_id;`

### `PATCH .../{id}/reschedule`
**Audit**: `UPDATE`
**Logic**: Update time, log reason, optionally trigger notification.
**SQL**: 
```sql
UPDATE appointments 
SET scheduled_at = :new_time, 
    notes = CONCAT(notes, '\nRescheduled from ', scheduled_at, ' to ', :new_time, '. Reason: ', :reason),
    updated_at = NOW() 
WHERE id = :id AND organization_id = :org_id;
```
 
### `DELETE .../{id}`
**Audit**: `CANCEL`
**SQL**: `UPDATE appointments SET status = 'CANCELLED', cancellation_reason = :reason, updated_at = NOW() WHERE id = :id AND organization_id = :org_id;`

---

## 15. Messaging

### `GET /api/organizations/{org_id}/messages`
**SQL**:
```sql
SELECT mt.*, 
       (SELECT json_build_object('body', body, 'sent_at', created_at) 
        FROM messages WHERE thread_id = mt.id ORDER BY created_at DESC LIMIT 1) as last_message
FROM message_threads mt
JOIN message_participants mp ON mt.id = mp.thread_id
WHERE mt.organization_id = :org_id AND mp.user_id = :user_id AND mt.deleted_at IS NULL
ORDER BY mt.updated_at DESC
LIMIT :limit OFFSET :offset;
```

### `POST .../messages` (Start Thread)
**Audit**: `CREATE`
**SQL**: Transact `INSERT INTO message_threads`, `message_participants` (x2), `messages`.

### `GET .../messages/{id}`
**Audit**: `READ`
**SQL**: `SELECT * FROM messages WHERE thread_id = :id ORDER BY created_at ASC;`

### `POST .../replies`
**Audit**: `CREATE`
**SQL**: `INSERT INTO messages (thread_id, sender_id, body) VALUES (...); UPDATE message_threads SET updated_at = NOW() WHERE id = :thread_id;`

---

## 16. Documents

### `POST .../upload-url`
**Audit**: `CREATE`
**Logic**: S3 Presigned PUT.
**SQL**: `INSERT INTO documents (organization_id, patient_id, s3_key, scan_status) VALUES (...);`

### `GET .../documents`
**Audit**: `LIST`
**SQL**: `SELECT * FROM documents WHERE organization_id = :org_id AND patient_id = :patient_id AND deleted_at IS NULL;`

### `GET .../documents/{id}/download-url`
**Audit**: `DOWNLOAD`
**Logic**: 
1. Verify document exists and belongs to org.
2. Generate S3 Presigned GET.
**SQL**: 
```sql
SELECT 1 FROM documents 
WHERE id = :id AND organization_id = :org_id AND deleted_at IS NULL;
```

### `DELETE .../documents/{id}`
**Audit**: `DELETE`
**SQL**: `UPDATE documents SET deleted_at = NOW() WHERE id = :id;`

---

## 17. Call Center

### `GET /api/call-center/queue`
**Performance**: Requires index `idx_calls_org_status_queue` (composite) or standard filtering.
**SQL**: 
```sql
SELECT * FROM calls 
WHERE organization_id = :org_id AND status = 'QUEUED' 
ORDER BY entered_queue_at ASC
LIMIT :limit OFFSET :offset;
```

### `POST .../outbound`
**Logic**: Safety Check `contact_methods.is_safe_for_voicemail`.
**SQL**: `INSERT INTO calls (call_type, status, ...) VALUES ('OUTBOUND', 'INITIATING', ...);`

### `GET /api/call-center/calls/{call_id}`
**Audit**: `READ` (Detailed)
**SQL**:
```sql
SELECT c.*, u.display_name as agent_name, p.first_name, p.last_name
FROM calls c
LEFT JOIN users u ON c.agent_id = u.id
LEFT JOIN patients p ON c.patient_id = p.id
WHERE c.id = :call_id AND c.organization_id = :org_id;
```

### `PATCH /api/call-center/calls/{call_id}`
**Audit**: `UPDATE`
**SQL**: 
```sql
UPDATE calls 
SET outcome = :outcome, notes = :notes, patient_id = :patient_id, updated_at = NOW() 
WHERE id = :call_id AND organization_id = :org_id;
```

### `GET /api/call-center/calls/{call_id}/recording-url`
**Audit**: `DOWNLOAD` / `LISTEN`
**Logic**: Verify `recording_url` exists in DB. Generate Presigned GET for S3.

### `GET /api/call-center/patients/{patient_id}/call-history`
**Audit**: `READ`
**SQL**:
```sql
SELECT c.*, u.display_name as agent_name
FROM calls c
LEFT JOIN users u ON c.agent_id = u.id
WHERE c.patient_id = :patient_id AND c.organization_id = :org_id
ORDER BY c.started_at DESC
LIMIT :limit OFFSET :offset;
```

### `POST /api/call-center/calls/{call_id}/tasks`
**Audit**: `CREATE_TASK`
**SQL**:
```sql
INSERT INTO tasks (organization_id, assignee_id, related_resource_type, related_resource_id, description, due_at, status, created_by)
VALUES (:org_id, :assignee_id, 'CALL', :call_id, :description, :due_at, 'PENDING', :user_id)
RETURNING id;
```

---

## 18. Support

### `POST /api/support/tickets`
**SQL**: `INSERT INTO support_tickets (user_id, organization_id, subject, body, category) VALUES (...);`

### `GET /api/support/tickets`
**SQL**: `SELECT * FROM support_tickets WHERE user_id = :user_id ORDER BY created_at DESC;`

### `GET /api/support/tickets/{ticket_id}`
**Auth**: Ticket Owner Only.
**SQL**: 
```sql
SELECT st.*, 
       (SELECT json_agg(json_build_object(
           'id', sm.id, 
           'body', sm.body, 
           'sender_id', sm.sender_id,
           'created_at', sm.created_at,
           'is_internal', sm.is_internal_note
       ) ORDER BY sm.created_at ASC) 
        FROM support_messages sm 
        WHERE sm.ticket_id = st.id AND (sm.is_internal_note IS FALSE OR :is_admin IS TRUE)) as messages
FROM support_tickets st 
WHERE st.id = :ticket_id AND st.user_id = :user_id;
```

### `POST /api/support/tickets/{ticket_id}/messages`
**Auth**: Ticket Owner Only.
**SQL**:
```sql
INSERT INTO support_messages (ticket_id, sender_id, body, attachment_document_id)
VALUES (:ticket_id, :user_id, :body, :attachment_id)
RETURNING id, created_at;
-- Trigger notification to support team logic here
```

---

## 19. Admin & Super Admin

### `POST /api/admin/impersonate/{patient_id}`
**Audit**: `BREAK_GLASS` (CRITICAL)
**SQL**: 
```sql
-- 1. Verify Patient belongs to Admin's Organization
SELECT 1 FROM organization_patients 
WHERE organization_id = :org_id AND patient_id = :patient_id AND status = 'ACTIVE';
-- 2. Log Break Glass
INSERT INTO audit_logs (actor_user_id, organization_id, resource_type, resource_id, action_type, occurred_at)
VALUES (:user_id, :org_id, 'IMPERSONATION', :patient_id, 'BREAK_GLASS', NOW());
```
**Logic**: Generate JWT with `act_as: patient_id`.

### `GET /api/admin/audit-logs`
**SQL**: 
```sql
SELECT * FROM audit_logs 
WHERE organization_id = :org_id 
ORDER BY occurred_at DESC 
LIMIT :limit OFFSET :offset;
```

### `GET /api/admin/audit-logs/export`
**SQL**: 
```sql
SELECT * FROM audit_logs 
WHERE organization_id = :org_id 
ORDER BY occurred_at DESC;
-- Note: Streaming response for CSV
```

### `GET /api/super-admin/organizations`
**SQL**:
```sql
SELECT * FROM organizations 
WHERE (:status IS NULL OR subscription_status = :status)
LIMIT :limit OFFSET :offset;
```

### `GET /api/super-admin/users`
**SQL**: 
```sql
SELECT id, email, display_name, is_super_admin, mfa_enabled, last_login_at, created_at, failed_login_attempts, locked_until 
FROM users 
WHERE (:search IS NULL OR email ILIKE :search)
LIMIT :limit OFFSET :offset;
```

### `GET /api/super-admin/users/{user_id}`
**SQL**: `SELECT * FROM users WHERE id = :user_id;`

### `POST /api/super-admin/users/{user_id}/unlock`
**Audit**: `UNLOCK_ACCOUNT`
**SQL**:
```sql
UPDATE users 
SET failed_login_attempts = 0, locked_until = NULL, updated_at = NOW() 
WHERE id = :user_id;
```

### `POST /api/super-admin/users/{user_id}/suspend`
**Audit**: `SUSPEND_ACCOUNT`
**SQL**:
```sql
UPDATE users SET locked_until = 'infinity', updated_at = NOW() WHERE id = :user_id; 
```

### `GET /api/super-admin/system/health`
**Logic**: 
1. `SELECT 1` (DB)
2. `PING` (Redis)
3. Return JSON.

---

## 20. Webhooks & AI

### `POST /api/webhooks/stripe`
**Logic**: `stripe.Webhook.construct_event`. Handle `checkout.session.completed` -> `UPDATE organizations SET subscription_status = 'ACTIVE'`.

### `POST /api/organizations/{org_id}/ai/summarize`
**Logic**: Fetch clinical notes SQL -> Call Vertex AI -> Return text. **NO STORAGE**.

---

## 21. Consent & Compliance

### `GET /api/consent/required`
**Logic**: Check if user has signed latest versions.
**SQL**:
```sql
SELECT t.type, t.version 
FROM (VALUES ('HIPAA_NOTICE', 'v2.1'), ('TERMS_OF_SERVICE', 'v3.0')) AS t(type, version)
EXCEPT
SELECT consent_type, version_string 
FROM consents 
WHERE patient_id = :current_patient_id; 
```

### `GET /api/consent/documents/{document_id}/content`
**Logic**: Return static text/markdown based on type/version.

### `POST /api/consent`
**Audit**: `SIGN_CONSENT`
**SQL**:
```sql
INSERT INTO consents (patient_id, consent_type, version_string, ip_address) 
VALUES (:patient_id, :type, :version, :ip_address);
UPDATE users SET requires_consent = FALSE WHERE id = :user_id; -- Update cache flag if exists
```

### `GET /api/consent/history`
**SQL**: `SELECT * FROM consents WHERE patient_id = :patient_id ORDER BY agreed_at DESC;`

---

## 22. Billing & Subscriptions

### `POST /api/organizations/{org_id}/billing/checkout`
**Logic**: Create Stripe Session (Mode: Subscription).
**SQL**: `SELECT stripe_customer_id FROM organizations WHERE id = :org_id;`

### `POST /api/organizations/{org_id}/billing/portal`
**Logic**: Create Stripe Billing Portal Session.
**SQL**: `SELECT stripe_customer_id FROM organizations WHERE id = :org_id;`

### `POST /api/organizations/{org_id}/patients/{patient_id}/billing/checkout`
**Logic**: Create Stripe Session (Mode: Subscription) for Patient.
**SQL**: `SELECT stripe_customer_id FROM patients WHERE id = :patient_id;`

### `POST /api/organizations/{org_id}/patients/{patient_id}/billing/portal`
**Logic**: Create Stripe Billing Portal Session.
**SQL**: `SELECT stripe_customer_id FROM patients WHERE id = :patient_id;`

---

## 23. Health Checks & System

### `GET /health`
**Logic**: Return 200 OK.

### `GET /health/deep`
**Logic**: Connectivity check.
1. DB: `SELECT 1`
2. Redis: `PING`

### `GET /api/organizations/{org_id}/events`
**Logic**: SSE Stream for Org Events (Admin).
**Events**: `member.joined`, `subscription.updated`, `license.expiring`.

### `GET /api/events`
**Summary**: User-scoped SSE Stream.
**Logic**: 
1. Validate Token.
2. Subscribe to Redis channels: `user:{user_id}`, `org:{org_id}:public`.
3. Stream events: `notification.new`, `message.new`, `appointment.reminder`.

---

## 24. Analytics

### `POST /api/telemetry`
**Summary**: Log behavioral events.
**SQL**:
```sql
INSERT INTO telemetry_events (user_id, event_name, properties, ip_address, user_agent)
VALUES (:user_id, :event_name, :properties, :ip_address, :user_agent);
```
