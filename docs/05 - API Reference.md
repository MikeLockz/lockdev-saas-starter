# API Reference - Lockdev SaaS Starter

This document provides a comprehensive reference for all API endpoints in the Lockdev platform. All endpoints return JSON and require authentication unless otherwise noted.

> [!NOTE]
> This reference is derived from the implementation plan. The live OpenAPI specification is auto-generated at `/docs` (Swagger UI) or `/redoc` (ReDoc).

**Related Documentation:**
- [Frontend Views & Routes](./06%20-%20Frontend%20Views%20%26%20Routes.md) — UI routes that consume these APIs
- [Implementation Plan](./03%20-%20Implementation.md) — Technical implementation details
- [Database Schema](./04%20-%20sql.ddl) — Underlying data model

---

## Table of Contents

1. [Base URL](#base-url)
2. [Authentication](#authentication)
3. [API Versioning](#api-versioning)
4. [Request Tracing](#request-tracing)
5. [Idempotency](#idempotency)
6. [Rate Limiting](#rate-limiting)
7. [Error Responses](#error-responses)
8. [Health Check](#health-check)
9. [Users & Authentication](#users--authentication)
10. [User Sessions](#user-sessions)
11. [Notifications](#notifications)
12. [MFA (Multi-Factor Authentication)](#mfa-multi-factor-authentication)
13. [Organizations (Tenants)](#organizations-tenants)
14. [Organization Members](#organization-members)
15. [Invitations](#invitations)
16. [Patients](#patients)
17. [Contact Methods](#contact-methods)
18. [Organization-Patient Relationships](#organization-patient-relationships)
19. [Providers](#providers)
20. [Staff](#staff)
21. [Proxies & Patient Assignments](#proxies--patient-assignments)
22. [Care Team](#care-team)
23. [Appointments](#appointments)
24. [Messaging](#messaging)
25. [Call Center](#call-center)
26. [Consent & Compliance](#consent--compliance)
27. [Documents](#documents)
28. [Billing & Subscriptions](#billing--subscriptions)
29. [Real-Time Events (SSE)](#real-time-events-sse)
30. [Admin Endpoints](#admin-endpoints)
31. [Super Admin Endpoints](#super-admin-endpoints)
32. [Support](#support)
33. [Analytics](#analytics)
34. [Webhooks](#webhooks)
35. [AI Services](#ai-services)
36. [Appendix: ID Formats](#appendix-id-formats)
36. [Appendix: PHI Access Matrix](#appendix-phi-access-matrix)
37. [Appendix: Audit Log Triggers](#appendix-audit-log-triggers)
38. [Appendix: OpenAPI Specification](#appendix-openapi-specification)

---

## Base URL

| Environment | URL |
|-------------|-----|
| Local | `http://localhost:8000` |
| Staging | `https://api-staging.lockdev.com` |
| Production | `https://api.lockdev.com` |

---

## Authentication

All protected endpoints require a Firebase/GCIP JWT token in the `Authorization` header:

```
Authorization: Bearer <firebase_id_token>
```

### Token Claims
| Claim | Description |
|-------|-------------|
| `sub` | Firebase UID (maps to `users.id`) |
| `email` | User email address |
| `act_as` | (Impersonation) Patient ID being impersonated |
| `impersonator_id` | (Impersonation) Admin ID performing impersonation |

### Example Request
```bash
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIs..."
```

---

## API Versioning

This API does **NOT** use URL path versioning (e.g., `/v1/`, `/v2/`).

### Versioning Policy

**Breaking changes** are:
- Announced **90 days in advance** via email to all registered developers
- Documented in the [Changelog](#changelog)
- Communicated with migration guides where applicable

**Non-breaking changes** (deployed without versioning):
- New optional request fields
- New response fields (additive only)
- New endpoints
- New enum values in response fields

> [!TIP]
> Design your client to ignore unknown response fields to ensure forward compatibility.

---

## Request Tracing

Every response includes an `X-Request-ID` header for debugging and support:

```http
HTTP/1.1 200 OK
X-Request-ID: 01HQ7V60-abc123-xyz789
Content-Type: application/json
```

### Using Request IDs

1. **Debugging**: Include the `X-Request-ID` when contacting support for faster issue resolution
2. **Correlation**: Pass your own `X-Request-ID` header in requests to correlate with your logs
3. **Distributed Tracing**: The request ID is propagated to all downstream services and appears in audit logs

**Example with custom request ID:**
```bash
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Request-ID: my-custom-trace-id-12345"
```

---

## Idempotency

For `POST` requests that create resources, include an `Idempotency-Key` header to prevent duplicate creation on network retries:

```http
POST /api/organizations/{org_id}/patients HTTP/1.1
Authorization: Bearer <token>
Idempotency-Key: user-provided-unique-key-123
Content-Type: application/json
```

### Idempotency Rules

| Rule | Description |
|------|-------------|
| **Key Format** | Any string up to 255 characters (UUIDs recommended) |
| **Key Lifetime** | Valid for 24 hours after first use |
| **Scope** | Per-user, per-endpoint |
| **Replay Behavior** | Returns cached response with `X-Idempotent-Replayed: true` header |

### Supported Endpoints

- `POST /api/organizations/{org_id}/patients`
- `POST /api/organizations/{org_id}/appointments`
- `POST /api/organizations/{org_id}/messages`
- `POST /api/organizations/{org_id}/documents/upload-url`
- `POST /api/organizations/{org_id}/billing/checkout`

**Example:**
```bash
# First request - creates the patient
curl -X POST "http://localhost:8000/api/organizations/01HQ7V3Y.../patients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: patient-create-$(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", "dob": "1985-03-15"}'

# Retry with same key - returns same response, no duplicate created
curl -X POST "http://localhost:8000/api/organizations/01HQ7V3Y.../patients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: patient-create-$(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", "dob": "1985-03-15"}'
```

---

## Rate Limiting

Default rate limit: `100 requests/minute` per IP address.

| Endpoint Category | Limit |
|-------------------|-------|
| General API | 100/minute |
| Auth endpoints | 20/minute |
| Health checks | Unlimited |
| Webhooks | 1000/minute |

Responses include headers:
- `X-RateLimit-Limit`: Max requests per window
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE",
  "status_code": 400
}
```

### Common Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `CONSENT_REQUIRED` | 403 | User must accept TOS/HIPAA |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists or state conflict |
| `VALIDATION_ERROR` | 422 | Invalid request body |
| `RATE_LIMITED` | 429 | Too many requests |
| `MFA_REQUIRED` | 403 | Staff must enable MFA |

### Domain-Specific Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `PROXY_ACCESS_EXPIRED` | 403 | Proxy assignment has expired |
| `PROXY_PERMISSION_DENIED` | 403 | Proxy lacks required permission for this action |
| `VOICEMAIL_UNSAFE` | 400 | Contact marked unsafe for voicemail/SMS |
| `DUPLICATE_MRN` | 409 | Medical record number already exists in organization |
| `LICENSE_EXPIRED` | 400 | Provider license has expired |
| `SUBSCRIPTION_REQUIRED` | 402 | Organization subscription inactive or required |
| `PATIENT_DISCHARGED` | 400 | Patient has been discharged from organization |
| `IMPERSONATION_EXPIRED` | 403 | Impersonation session has expired |
| `INVITATION_EXPIRED` | 400 | Invitation token has expired |
| `INVITATION_USED` | 400 | Invitation has already been accepted |

### Example Error Response (Consent Required)
```json
{
  "detail": "Consent documents require signature before accessing the platform",
  "code": "CONSENT_REQUIRED",
  "status_code": 403,
  "pending_documents": ["HIPAA_NOTICE", "TERMS_OF_SERVICE"]
}
```

---

## Health Check

### `GET /health`
Shallow health check - returns 200 if the web server is up.

**Authentication:** None

**Response:**
```json
{
  "status": "ok"
}
```

---

### `GET /health/deep`
Deep health check - verifies database and Redis connectivity.

**Authentication:** None

**Response (Healthy):**
```json
{
  "status": "healthy",
  "database": "ok",
  "redis": "ok"
}
```

**Response (Unhealthy):**
```json
{
  "status": "unhealthy",
  "errors": ["database: connection refused"]
}
```

---

## Users & Authentication

### `GET /api/users/me`
Get the current authenticated user's profile and role information.

**Authentication:** Required

**Related Endpoints:**
- [`PATCH /api/users/me`](#patch-apiusersme) — Update profile
- [`GET /api/users/me/communication-preferences`](#get-apiusersmecommunication-preferences) — Get preferences

**Response:**
```json
{
  "id": "01HQ7V3X...",
  "email": "user@example.com",
  "display_name": "John Doe",
  "mfa_enabled": true,
  "requires_consent": false,
  "roles": [
    {
      "organization_id": "01HQ7V3Y...",
      "organization_name": "ACME Clinic",
      "role": "PROVIDER",
      "role_entity_id": "01HQ7V3Z..."
    }
  ],
  "patient_profile": {
    "id": "01HQ7V40...",
    "is_self_managed": true
  },
  "proxy_profile": {
    "id": "01HQ7V41...",
    "managed_patients": [
      {"id": "01HQ7V42...", "name": "John Doe Jr."}
    ]
  }
}
```

**Example curl:**
```bash
curl -X GET "https://api.lockdev.com/api/users/me" \
  -H "Authorization: Bearer $FIREBASE_TOKEN" \
  -H "Content-Type: application/json"
```

---

### `PATCH /api/users/me`
Update current user's profile.

**Authentication:** Required

**Request Body:**
```json
{
  "display_name": "Jonathan Doe"
}
```

**Response:**
```json
{
  "id": "01HQ7V3X...",
  "email": "user@example.com",
  "display_name": "Jonathan Doe",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### `POST /api/users/device-token`
Register an FCM token for push notifications.

**Authentication:** Required

**Request Body:**
```json
{
  "token": "fcm_device_token_string",
  "platform": "ios"
}
```

| Field | Type | Required | Values |
|-------|------|----------|--------|
| `token` | string | Yes | FCM device token |
| `platform` | string | Yes | `ios`, `android`, `web` |

**Response:**
```json
{
  "success": true
}
```

---

### `DELETE /api/users/device-token`
Remove an FCM token (logout cleanup).

**Authentication:** Required

**Request Body:**
```json
{
  "token": "fcm_device_token_string"
}
```

**Response:**
```json
{
  "success": true
}
```

---

### `GET /api/users/me/communication-preferences`
Get user's communication opt-in status.

**Authentication:** Required

**Related Endpoints:**
- [`PATCH /api/users/me/communication-preferences`](#patch-apiusersmecommunication-preferences) — Update preferences

**Response:**
```json
{
  "transactional_consent": true,
  "marketing_consent": false,
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### `PATCH /api/users/me/communication-preferences`
Update communication preferences.

**Authentication:** Required

**Request Body:**
```json
{
  "transactional_consent": true,
  "marketing_consent": true
}
```

> [!NOTE]
> Per TCPA compliance, `transactional_consent` must be `true` for appointment reminders and billing alerts. `marketing_consent` controls promotional communications.

**Response:**
```json
{
  "transactional_consent": true,
  "marketing_consent": true,
  "updated_at": "2024-01-15T10:31:00Z"
}
```

---

## User Sessions

Manage active user sessions and account-level operations.

**Related Endpoints:**
- [Users & Authentication](#users--authentication) — User profile
- [MFA](#mfa-multi-factor-authentication) — Security settings

### `GET /api/users/me/sessions`
List all active sessions for the current user.

**Authentication:** Required

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V53...",
      "device": "Chrome on macOS",
      "ip_address": "192.168.1.1",
      "location": "San Francisco, CA",
      "is_current": true,
      "created_at": "2024-01-15T10:30:00Z",
      "last_active_at": "2024-01-15T11:45:00Z"
    },
    {
      "id": "01HQ7V54...",
      "device": "Safari on iPhone",
      "ip_address": "10.0.0.50",
      "location": "San Francisco, CA",
      "is_current": false,
      "created_at": "2024-01-14T08:00:00Z",
      "last_active_at": "2024-01-14T18:30:00Z"
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

---

### `DELETE /api/users/me/sessions/{session_id}`
Terminate a specific session.

**Authentication:** Required

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | ULID | Session to terminate |

> [!WARNING]
> If `session_id` matches the current session, this is equivalent to logout.

**Response:**
```json
{
  "success": true,
  "terminated_at": "2024-01-15T10:40:00Z"
}
```

---

### `POST /api/users/me/export`
Request a data export (HIPAA Right of Access).

**Authentication:** Required

> [!NOTE]
> This initiates a background job. The user receives an email with a secure download link when the export is ready (typically 24-48 hours).

**Request Body:**
```json
{
  "format": "json",
  "include_documents": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `format` | string | No | `json` (default) or `pdf` |
| `include_documents` | boolean | No | Include uploaded documents (default: false) |

**Response:**
```json
{
  "export_id": "01HQ7V55...",
  "status": "PENDING",
  "estimated_completion": "2024-01-16T10:30:00Z"
}
```

---

### `DELETE /api/users/me`
Delete user account (soft delete for HIPAA compliance).

**Authentication:** Required

> [!CAUTION]
> This performs a soft delete. The user's data is retained for legal compliance but the account becomes inaccessible. This action cannot be undone.

**Request Body:**
```json
{
  "password": "current_password",
  "reason": "No longer using the service"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `password` | string | Yes | Current password for verification |
| `reason` | string | No | Optional deletion reason |

**Response:**
```json
{
  "success": true,
  "deleted_at": "2024-01-15T10:40:00Z"
}
```

---

## Notifications

Manage user notifications for appointments, messages, and system events.

**Related Endpoints:**
- [Users & Authentication](#users--authentication) — User profile
- [Real-Time Events](#real-time-events-sse) — Live notification delivery

### `GET /api/users/me/notifications`
List notifications for the current user.

**Authentication:** Required

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter` | string | — | `unread` to show only unread |
| `type` | string | — | `appointment`, `message`, `billing`, `system`, `admin` |
| `limit` | int | 50 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7VC0...",
      "type": "appointment",
      "title": "Appointment Reminder",
      "body": "Your appointment with Dr. Smith is tomorrow at 2:00 PM",
      "is_read": false,
      "action_url": "/appointments/01HQ7V90...",
      "metadata": {
        "appointment_id": "01HQ7V90...",
        "provider_name": "Dr. Jane Smith"
      },
      "created_at": "2024-01-19T10:00:00Z"
    },
    {
      "id": "01HQ7VC1...",
      "type": "message",
      "title": "New Message",
      "body": "Dr. Smith replied to your message",
      "is_read": true,
      "action_url": "/messages/01HQ7VA0...",
      "metadata": {
        "thread_id": "01HQ7VA0...",
        "sender_name": "Dr. Jane Smith"
      },
      "created_at": "2024-01-15T14:30:00Z"
    }
  ],
  "total": 25,
  "unread_count": 5,
  "limit": 50,
  "offset": 0
}
```

---

### `PATCH /api/users/me/notifications/{notification_id}`
Update notification status (mark read/unread).

**Authentication:** Required

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `notification_id` | ULID | Notification ID |

**Request Body:**
```json
{
  "is_read": true
}
```

**Response:**
```json
{
  "id": "01HQ7VC0...",
  "is_read": true,
  "updated_at": "2024-01-19T11:00:00Z"
}
```

---

### `POST /api/users/me/notifications/mark-all-read`
Mark all notifications as read.

**Authentication:** Required

**Request Body:**
```json
{
  "before": "2024-01-19T12:00:00Z"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `before` | datetime | No | Only mark notifications before this time (default: now) |

**Response:**
```json
{
  "success": true,
  "marked_count": 12,
  "updated_at": "2024-01-19T12:00:00Z"
}
```

---

### `DELETE /api/users/me/notifications/{notification_id}`
Delete a notification (soft delete - removes from user's list).

**Authentication:** Required

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `notification_id` | ULID | Notification ID |

**Response:**
```json
{
  "success": true,
  "deleted_at": "2024-01-19T12:05:00Z"
}
```

---

## MFA (Multi-Factor Authentication)

Manage multi-factor authentication for user accounts.

> [!IMPORTANT]
> MFA is **mandatory** for Staff, Provider, and Admin roles before accessing PHI routes.

**Related Endpoints:**
- [User Sessions](#user-sessions) — Session management
- [Users & Authentication](#users--authentication) — User profile

### `POST /api/users/me/mfa/setup`
Initialize MFA setup. Returns a QR code for authenticator apps.

**Authentication:** Required

**Response:**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code_url": "data:image/png;base64,iVBORw0KGgo...",
  "backup_codes": [
    "A1B2-C3D4",
    "E5F6-G7H8",
    "I9J0-K1L2",
    "M3N4-O5P6",
    "Q7R8-S9T0",
    "U1V2-W3X4",
    "Y5Z6-A7B8",
    "C9D0-E1F2"
  ],
  "expires_at": "2024-01-15T10:45:00Z"
}
```

> [!WARNING]
> The `backup_codes` are shown only once. Users must save them securely before proceeding.

---

### `POST /api/users/me/mfa/verify`
Complete MFA setup by verifying a TOTP code.

**Authentication:** Required

**Request Body:**
```json
{
  "code": "123456"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | 6-digit TOTP code from authenticator app |

**Response (Success):**
```json
{
  "success": true,
  "mfa_enabled": true,
  "enabled_at": "2024-01-15T10:35:00Z"
}
```

**Response (Failure):**
```json
{
  "detail": "Invalid verification code",
  "code": "INVALID_MFA_CODE",
  "status_code": 400
}
```

---

### `POST /api/users/me/mfa/backup-codes`
Regenerate backup codes (invalidates all existing codes).

**Authentication:** Required (MFA must be enabled)

**Request Body:**
```json
{
  "password": "current_password"
}
```

**Response:**
```json
{
  "backup_codes": [
    "X1Y2-Z3A4",
    "B5C6-D7E8",
    "F9G0-H1I2",
    "J3K4-L5M6",
    "N7O8-P9Q0",
    "R1S2-T3U4",
    "V5W6-X7Y8",
    "Z9A0-B1C2"
  ],
  "generated_at": "2024-01-15T10:35:00Z"
}
```

> [!CAUTION]
> All previous backup codes are immediately invalidated when new codes are generated.

---

### `DELETE /api/users/me/mfa`
Disable MFA for the account.

**Authentication:** Required (password confirmation)

> [!WARNING]
> Staff/Provider/Admin roles cannot disable MFA as it is mandatory for PHI access.

**Request Body:**
```json
{
  "password": "current_password"
}
```

**Response:**
```json
{
  "success": true,
  "mfa_disabled_at": "2024-01-15T10:40:00Z"
}
```

**Error Response (Role Restriction):**
```json
{
  "detail": "MFA cannot be disabled for your role",
  "code": "MFA_REQUIRED_FOR_ROLE",
  "status_code": 403
}
```

---

## Organizations (Tenants)

### `GET /api/organizations`
List organizations the current user belongs to.

**Authentication:** Required

**Related Endpoints:**
- [`POST /api/organizations`](#post-apiorganizations) — Create organization
- [`GET /api/organizations/{org_id}`](#get-apiorganizationsorg_id) — Get details
- [`GET /api/organizations/{org_id}/members`](#get-apiorganizationsorg_idmembers) — List members

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V3Y...",
      "name": "ACME Clinic",
      "role": "PROVIDER",
      "settings": {
        "logo_url": "https://...",
        "primary_color": "#1E40AF"
      }
    }
  ],
  "total": 1
}
```

---

### `POST /api/organizations`
Create a new organization (tenant).

**Authentication:** Required

> [!NOTE]
> The creating user automatically becomes an ADMIN member of the new organization.

**Request Body:**
```json
{
  "name": "New Healthcare Clinic",
  "tax_id": "XX-XXXXXXX",
  "settings": {
    "primary_color": "#1E40AF",
    "logo_url": "https://..."
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Organization display name |
| `tax_id` | string | No | EIN for billing purposes |
| `settings` | object | No | Custom branding settings |

**Response:** `201 Created`
```json
{
  "id": "01HQ7V3Y...",
  "name": "New Healthcare Clinic",
  "tax_id": "XX-XXXXXXX",
  "settings": {
    "primary_color": "#1E40AF",
    "logo_url": "https://..."
  },
  "subscription_status": "INCOMPLETE",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### `GET /api/organizations/{org_id}`
Get organization details.

**Authentication:** Required (Member of organization)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |

**Related Endpoints:**
- [`PATCH /api/organizations/{org_id}`](#patch-apiorganizationsorg_id) — Update settings
- [`GET /api/organizations/{org_id}/members`](#get-apiorganizationsorg_idmembers) — List members
- [`POST /api/organizations/{org_id}/billing/checkout`](#post-apiorganizationsorg_idbillingcheckout) — Start subscription

**Response:**
```json
{
  "id": "01HQ7V3Y...",
  "name": "ACME Clinic",
  "tax_id": "XX-XXXXXXX",
  "settings": {
    "logo_url": "https://...",
    "primary_color": "#1E40AF"
  },
  "subscription_status": "ACTIVE",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### `PATCH /api/organizations/{org_id}`
Update organization settings.

**Authentication:** Required (ADMIN role in organization)

**Request Body:**
```json
{
  "name": "ACME Health Clinic",
  "settings": {
    "primary_color": "#2563EB"
  }
}
```

**Response:**
```json
{
  "id": "01HQ7V3Y...",
  "name": "ACME Health Clinic",
  "settings": {
    "primary_color": "#2563EB"
  },
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### `DELETE /api/organizations/{org_id}`
Soft-delete an organization.

**Authentication:** Required (ADMIN role in organization)

> [!CAUTION]
> This performs a soft delete (`deleted_at` timestamp) for HIPAA compliance. All associated records are retained but the organization becomes inactive.

**Response:**
```json
{
  "success": true,
  "deleted_at": "2024-01-15T10:40:00Z"
}
```

---

## Organization Members

Manage users within an organization and their role assignments.

**Related Endpoints:**
- [Organizations](#organizations-tenants) — Parent resource
- [Providers](#providers) — Provider role details
- [Staff](#staff) — Staff role details

### `GET /api/organizations/{org_id}/members`
List all members of an organization.

**Authentication:** Required (Member of organization)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `role` | string | — | Filter by role: `ADMIN`, `PROVIDER`, `STAFF` |
| `search` | string | — | Search by name or email |
| `limit` | int | 50 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V60...",
      "user_id": "01HQ7V3X...",
      "email": "jane@example.com",
      "display_name": "Dr. Jane Smith",
      "role": "PROVIDER",
      "role_entity_id": "01HQ7V44...",
      "mfa_enabled": true,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "01HQ7V61...",
      "user_id": "01HQ7V3Y...",
      "email": "admin@example.com",
      "display_name": "Admin User",
      "role": "ADMIN",
      "role_entity_id": null,
      "mfa_enabled": true,
      "created_at": "2024-01-10T09:00:00Z"
    }
  ],
  "total": 15,
  "limit": 50,
  "offset": 0
}
```

---

### `POST /api/organizations/{org_id}/members`
Invite a new member to the organization.

**Authentication:** Required (ADMIN role in organization)

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "role": "STAFF",
  "send_invitation": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Email of user to invite |
| `role` | string | Yes | `ADMIN`, `PROVIDER`, or `STAFF` |
| `send_invitation` | boolean | No | Send email invite (default: true) |

**Response:** `201 Created`
```json
{
  "id": "01HQ7V62...",
  "user_id": null,
  "email": "newuser@example.com",
  "role": "STAFF",
  "status": "PENDING",
  "invitation_sent_at": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### `PATCH /api/organizations/{org_id}/members/{member_id}`
Update a member's role.

**Authentication:** Required (ADMIN role in organization)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |
| `member_id` | ULID | Membership ID |

**Request Body:**
```json
{
  "role": "ADMIN"
}
```

**Response:**
```json
{
  "id": "01HQ7V62...",
  "user_id": "01HQ7V3Z...",
  "role": "ADMIN",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### `DELETE /api/organizations/{org_id}/members/{member_id}`
Remove a member from the organization.

**Authentication:** Required (ADMIN role in organization)

> [!WARNING]
> This action is immediate and removes all access. The user's data in audit logs is retained.

**Response:**
```json
{
  "success": true,
  "removed_at": "2024-01-15T10:40:00Z"
}
```

---

## Invitations

Manage organization member invitations.

**Related Endpoints:**
- [Organization Members](#organization-members) — Member management
- [Organizations](#organizations-tenants) — Parent resource

### `GET /api/organizations/{org_id}/invitations`
List all pending invitations for an organization.

**Authentication:** Required (ADMIN role in organization)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | `PENDING` | Filter: `PENDING`, `ACCEPTED`, `DECLINED`, `EXPIRED`, `ALL` |
| `limit` | int | 50 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V65...",
      "email": "newuser@example.com",
      "role": "PROVIDER",
      "status": "PENDING",
      "inviter_name": "Dr. Jane Smith",
      "inviter_email": "jane@acmeclinic.com",
      "expires_at": "2024-01-22T10:30:00Z",
      "created_at": "2024-01-15T10:30:00Z",
      "resend_count": 0
    },
    {
      "id": "01HQ7V66...",
      "email": "another@example.com",
      "role": "STAFF",
      "status": "ACCEPTED",
      "inviter_name": "Dr. Jane Smith",
      "inviter_email": "jane@acmeclinic.com",
      "accepted_at": "2024-01-16T09:00:00Z",
      "created_at": "2024-01-14T10:30:00Z",
      "resend_count": 1
    }
  ],
  "total": 15,
  "limit": 50,
  "offset": 0
}
```

---

### `POST /api/organizations/{org_id}/invitations/{invitation_id}/resend`
Resend an invitation email.

**Authentication:** Required (ADMIN role in organization)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |
| `invitation_id` | ULID | Invitation ID |

> [!NOTE]
> Resending an invitation extends the expiration by 7 days from the current time.

**Response:**
```json
{
  "success": true,
  "resent_at": "2024-01-17T10:30:00Z",
  "new_expires_at": "2024-01-24T10:30:00Z",
  "resend_count": 2
}
```

**Error Responses:**
| Code | Description |
|------|-------------|
| `INVITATION_ACCEPTED` | Cannot resend — invitation already accepted |
| `INVITATION_DECLINED` | Cannot resend — invitation was declined |
| `RESEND_LIMIT_EXCEEDED` | Maximum of 5 resends per invitation |

---

### `DELETE /api/organizations/{org_id}/invitations/{invitation_id}`
Cancel a pending invitation.

**Authentication:** Required (ADMIN role in organization)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |
| `invitation_id` | ULID | Invitation ID |

> [!NOTE]
> Only `PENDING` invitations can be cancelled.

**Response:**
```json
{
  "success": true,
  "cancelled_at": "2024-01-17T10:30:00Z"
}
```

---

### `GET /api/invitations/{token}`
Get invitation details by token (for invitation acceptance flow).

**Authentication:** None required (token serves as authentication)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `token` | string | Invitation token (from email link) |

**Response:**
```json
{
  "organization_id": "01HQ7V3Y...",
  "organization_name": "ACME Clinic",
  "organization_logo_url": "https://...",
  "role": "PROVIDER",
  "inviter_name": "Dr. Jane Smith",
  "inviter_email": "jane@acmeclinic.com",
  "invited_email": "newuser@example.com",
  "expires_at": "2024-01-22T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
| Code | Description |
|------|-------------|
| `INVITATION_EXPIRED` | Token has expired |
| `INVITATION_USED` | Invitation already accepted |
| `INVITATION_NOT_FOUND` | Invalid token |

---

### `POST /api/invitations/{token}/accept`
Accept an organization invitation.

**Authentication:** Required (user must be logged in)

> [!NOTE]
> If the logged-in user's email doesn't match the invited email, the invitation still succeeds but is logged for audit purposes.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `token` | string | Invitation token |

**Response:**
```json
{
  "success": true,
  "organization_id": "01HQ7V3Y...",
  "organization_name": "ACME Clinic",
  "role": "PROVIDER",
  "member_id": "01HQ7V60...",
  "accepted_at": "2024-01-15T10:35:00Z"
}
```

---

### `POST /api/invitations/{token}/decline`
Decline an organization invitation.

**Authentication:** None required

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `token` | string | Invitation token |

**Response:**
```json
{
  "success": true,
  "declined_at": "2024-01-15T10:35:00Z"
}
```

---

## Patients

> [!IMPORTANT]
> All patient endpoints involve Protected Health Information (PHI) and trigger audit log entries for HIPAA compliance.

**Related Endpoints:**
- [Care Team](#care-team) — Patient's care team
- [Documents](#documents) — Patient documents
- [Proxies](#proxies--patient-assignments) — Proxy access

### `GET /api/organizations/{org_id}/patients`
List patients in an organization (Staff/Provider only).

**Authentication:** Required (PROVIDER, STAFF, or ADMIN role) 🔒

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | — | Search by name or MRN |
| `status` | string | — | Filter: `ACTIVE`, `DISCHARGED` |
| `limit` | int | 50 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V42...",
      "first_name": "John",
      "last_name": "Doe",
      "dob": "1985-03-15",
      "medical_record_number": "MRN-12345",
      "status": "ACTIVE"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

**Example curl:**
```bash
# List patients with search and pagination
curl -X GET "https://api.lockdev.com/api/organizations/01HQ7V3Y.../patients?search=Doe&status=ACTIVE&limit=10&offset=0" \
  -H "Authorization: Bearer $FIREBASE_TOKEN" \
  -H "Content-Type: application/json"
```

---

### `GET /api/organizations/{org_id}/patients/{patient_id}`
Get patient details.

**Authentication:** Required (PROVIDER, STAFF, or assigned Proxy) 🔒

> [!IMPORTANT]
> This endpoint triggers a `READ_ACCESS` audit log entry for HIPAA compliance.

**Related Endpoints:**
- [`GET /api/organizations/{org_id}/patients/{patient_id}/care-team`](#get-apiorganizationsorg_idpatientspatient_idcare-team) — Care team
- [`GET /api/organizations/{org_id}/patients/{patient_id}/documents`](#get-apiorganizationsorg_idpatientspatient_iddocuments) — Documents
- [`GET /api/organizations/{org_id}/patients/{patient_id}/proxies`](#get-apiorganizationsorg_idpatientspatient_idproxies) — Proxies
- [`POST /api/organizations/{org_id}/patients/{patient_id}/billing/checkout`](#post-apiorganizationsorg_idpatientspatient_idbillingcheckout) — Billing

**Response:**
```json
{
  "id": "01HQ7V42...",
  "user_id": "01HQ7V3X...",
  "first_name": "John",
  "last_name": "Doe",
  "dob": "1985-03-15",
  "medical_record_number": "MRN-12345",
  "legal_sex": "MALE",
  "subscription_status": "ACTIVE",
  "contact_methods": [
    {
      "id": "01HQ7V43...",
      "type": "MOBILE",
      "value": "+1-555-123-4567",
      "is_primary": true,
      "is_safe_for_voicemail": true
    }
  ],
  "care_team": [
    {
      "provider_id": "01HQ7V44...",
      "provider_name": "Dr. Jane Smith",
      "is_primary": true
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### `POST /api/organizations/{org_id}/patients`
Create a new patient record.

**Authentication:** Required (PROVIDER, STAFF, or ADMIN) 🔒

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "dob": "1985-03-15",
  "legal_sex": "MALE",
  "medical_record_number": "MRN-12345",
  "contact_methods": [
    {
      "type": "MOBILE",
      "value": "+1-555-123-4567",
      "is_primary": true,
      "is_safe_for_voicemail": true
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | string | Yes | Patient first name |
| `last_name` | string | Yes | Patient last name |
| `dob` | date | Yes | Date of birth (YYYY-MM-DD) |
| `legal_sex` | string | No | `MALE`, `FEMALE`, `OTHER` |
| `medical_record_number` | string | No | Internal MRN |
| `contact_methods` | array | No | Contact information |

**Response:** `201 Created` with patient object

**Example curl:**
```bash
curl -X POST "https://api.lockdev.com/api/organizations/01HQ7V3Y.../patients" \
  -H "Authorization: Bearer $FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: create-patient-$(uuidgen)" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "dob": "1985-03-15",
    "legal_sex": "MALE",
    "contact_methods": [{
      "type": "MOBILE",
      "value": "+1-555-123-4567",
      "is_primary": true,
      "is_safe_for_voicemail": true
    }]
  }'
```

---

### `PATCH /api/organizations/{org_id}/patients/{patient_id}`
Update patient information.

**Authentication:** Required (PROVIDER, STAFF, ADMIN, or patient self) 🔒

**Request Body:**
```json
{
  "first_name": "Jonathan",
  "contact_methods": [
    {
      "id": "01HQ7V43...",
      "type": "MOBILE",
      "value": "+1-555-987-6543",
      "is_primary": true,
      "is_safe_for_voicemail": false
    }
  ]
}
```

> [!NOTE]
> All fields are optional. Only provided fields are updated.

**Response:**
```json
{
  "id": "01HQ7V42...",
  "first_name": "Jonathan",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### `DELETE /api/organizations/{org_id}/patients/{patient_id}`
Soft-delete a patient record.

**Authentication:** Required (ADMIN only)

> [!CAUTION]
> This performs a soft delete (`deleted_at` timestamp) for HIPAA compliance. Records are retained but inaccessible.

**Response:**
```json
{
  "success": true,
  "deleted_at": "2024-01-15T10:40:00Z"
}
```

---

## Contact Methods

Manage patient contact information with safety flags.

> [!CAUTION]
> The `is_safe_for_voicemail` flag is **CRITICAL for patient safety**. Systems MUST check this flag before leaving voicemails or sending SMS messages to prevent disclosure in unsafe situations (e.g., domestic violence).

**Related Endpoints:**
- [Patients](#patients) — Parent resource

### `GET /api/organizations/{org_id}/patients/{patient_id}/contact-methods`
List all contact methods for a patient.

**Authentication:** Required (PROVIDER, STAFF, Patient self, or assigned Proxy) 🔒

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |
| `patient_id` | ULID | Patient ID |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V43...",
      "type": "MOBILE",
      "value": "+1-555-123-4567",
      "is_primary": true,
      "is_safe_for_voicemail": true,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "01HQ7V44...",
      "type": "EMAIL",
      "value": "patient@example.com",
      "is_primary": false,
      "is_safe_for_voicemail": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

---

### `POST /api/organizations/{org_id}/patients/{patient_id}/contact-methods`
Add a new contact method for a patient.

**Authentication:** Required (PROVIDER, STAFF, Patient self, or assigned Proxy) 🔒

**Request Body:**
```json
{
  "type": "MOBILE",
  "value": "+1-555-987-6543",
  "is_primary": false,
  "is_safe_for_voicemail": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | `MOBILE`, `HOME`, `WORK`, `EMAIL` |
| `value` | string | Yes | Phone number or email address |
| `is_primary` | boolean | No | Set as primary contact (default: false) |
| `is_safe_for_voicemail` | boolean | No | Safe for voicemail/SMS (default: false) |

> [!WARNING]
> Only one contact method per type can be marked as `is_primary`. Setting a new primary will unset the previous one.

**Response:** `201 Created`
```json
{
  "id": "01HQ7V45...",
  "type": "MOBILE",
  "value": "+1-555-987-6543",
  "is_primary": false,
  "is_safe_for_voicemail": false,
  "created_at": "2024-01-15T10:35:00Z"
}
```

---

### `PATCH /api/organizations/{org_id}/patients/{patient_id}/contact-methods/{contact_id}`
Update a contact method.

**Authentication:** Required (PROVIDER, STAFF, Patient self, or assigned Proxy) 🔒

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |
| `patient_id` | ULID | Patient ID |
| `contact_id` | ULID | Contact method ID |

**Request Body:**
```json
{
  "is_safe_for_voicemail": true,
  "is_primary": true
}
```

**Response:**
```json
{
  "id": "01HQ7V45...",
  "type": "MOBILE",
  "value": "+1-555-987-6543",
  "is_primary": true,
  "is_safe_for_voicemail": true,
  "updated_at": "2024-01-15T10:40:00Z"
}
```

---

### `DELETE /api/organizations/{org_id}/patients/{patient_id}/contact-methods/{contact_id}`
Remove a contact method.

**Authentication:** Required (PROVIDER, STAFF, or ADMIN) 🔒

> [!WARNING]
> Cannot delete the last remaining contact method for a patient.

**Response:**
```json
{
  "success": true,
  "deleted_at": "2024-01-15T10:45:00Z"
}
```

---

## Organization-Patient Relationships

Manage patient enrollment in organizations.

> [!NOTE]
> A patient can be enrolled in multiple organizations (e.g., primary care clinic and specialist office).

**Related Endpoints:**
- [Patients](#patients) — Patient records
- [Organizations](#organizations-tenants) — Organization details

### `GET /api/organizations/{org_id}/patients/{patient_id}/enrollment`
Get the patient's enrollment status in an organization.

**Authentication:** Required (PROVIDER, STAFF, or ADMIN) 🔒

**Response:**
```json
{
  "organization_id": "01HQ7V3Y...",
  "patient_id": "01HQ7V42...",
  "status": "ACTIVE",
  "enrolled_at": "2024-01-15T10:30:00Z",
  "discharged_at": null
}
```

---

### `POST /api/organizations/{org_id}/patients/{patient_id}/enrollment`
Enroll or re-enroll a patient in an organization.

**Authentication:** Required (PROVIDER, STAFF, or ADMIN) 🔒

**Request Body:**
```json
{
  "status": "ACTIVE"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | No | `ACTIVE` (default) or `DISCHARGED` |

**Response:** `201 Created`
```json
{
  "organization_id": "01HQ7V3Y...",
  "patient_id": "01HQ7V42...",
  "status": "ACTIVE",
  "enrolled_at": "2024-01-15T10:30:00Z"
}
```

---

### `PATCH /api/organizations/{org_id}/patients/{patient_id}/enrollment`
Update patient enrollment status (e.g., discharge).

**Authentication:** Required (PROVIDER, STAFF, or ADMIN) 🔒

**Request Body:**
```json
{
  "status": "DISCHARGED"
}
```

**Response:**
```json
{
  "organization_id": "01HQ7V3Y...",
  "patient_id": "01HQ7V42...",
  "status": "DISCHARGED",
  "enrolled_at": "2024-01-15T10:30:00Z",
  "discharged_at": "2024-06-15T14:00:00Z"
}
```

---

### `GET /api/patients/{patient_id}/organizations`
List all organizations a patient is enrolled in.

**Authentication:** Required (Patient self, assigned Proxy, or Super Admin) 🔒

> [!NOTE]
> This endpoint allows patients to see all their healthcare relationships across organizations.

**Response:**
```json
{
  "items": [
    {
      "organization_id": "01HQ7V3Y...",
      "organization_name": "ACME Primary Care",
      "status": "ACTIVE",
      "enrolled_at": "2024-01-15T10:30:00Z"
    },
    {
      "organization_id": "01HQ7V4A...",
      "organization_name": "Heart Specialists LLC",
      "status": "ACTIVE",
      "enrolled_at": "2024-03-01T09:00:00Z"
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

---

## Providers

Clinical providers within an organization.

**Related Endpoints:**
- [Organization Members](#organization-members) — Member management
- [Care Team](#care-team) — Provider-patient assignments

### `GET /api/organizations/{org_id}/providers`
List providers in an organization.

**Authentication:** Required (Member of organization)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `specialty` | string | — | Filter by specialty |
| `search` | string | — | Search by name or NPI |
| `limit` | int | 50 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V44...",
      "user_id": "01HQ7V45...",
      "name": "Dr. Jane Smith",
      "npi_number": "1234567890",
      "specialty": "Internal Medicine"
    }
  ],
  "total": 10,
  "limit": 50,
  "offset": 0
}
```

---

### `GET /api/organizations/{org_id}/providers/{provider_id}`
Get provider details.

**Authentication:** Required (Member of organization)

**Response:**
```json
{
  "id": "01HQ7V44...",
  "user_id": "01HQ7V45...",
  "npi_number": "1234567890",
  "dea_number": "AB1234567",
  "specialty": "Internal Medicine",
  "state_licenses": [
    {"state": "CA", "license_number": "A123456", "expiry": "2025-12-31"}
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### `POST /api/organizations/{org_id}/providers`
Create a provider profile for an existing member.

**Authentication:** Required (ADMIN role in organization)

**Request Body:**
```json
{
  "user_id": "01HQ7V45...",
  "npi_number": "1234567890",
  "specialty": "Internal Medicine",
  "dea_number": "AB1234567",
  "state_licenses": [
    {"state": "CA", "license_number": "A123456", "expiry": "2025-12-31"}
  ]
}
```

**Response:** `201 Created`
```json
{
  "id": "01HQ7V44...",
  "user_id": "01HQ7V45...",
  "npi_number": "1234567890",
  "specialty": "Internal Medicine",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### `PATCH /api/organizations/{org_id}/providers/{provider_id}`
Update provider details.

**Authentication:** Required (Provider themselves or ADMIN)

**Request Body:**
```json
{
  "npi_number": "1234567890",
  "specialty": "Family Medicine",
  "state_licenses": [
    {"state": "NY", "license_number": "222222", "expiry": "2026-01-01"}
  ]
}
```

**Response:**
```json
{
  "id": "01HQ7V44...",
  "specialty": "Family Medicine",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### `DELETE /api/organizations/{org_id}/providers/{provider_id}`
Remove a provider profile (soft delete).

**Authentication:** Required (ADMIN role in organization)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |
| `provider_id` | ULID | Provider ID |

> [!CAUTION]
> This performs a soft delete. The provider's data is retained for audit purposes but they lose access to the organization. Their user account remains active.

> [!NOTE]
> To completely remove a user from the organization, use `DELETE /api/organizations/{org_id}/members/{member_id}` instead.

**Response:**
```json
{
  "success": true,
  "deleted_at": "2024-01-15T10:40:00Z"
}
```

---

## Staff

Non-clinical staff members within an organization.

**Related Endpoints:**
- [Organization Members](#organization-members) — Member management

### `GET /api/organizations/{org_id}/staff`
List staff members in an organization.

**Authentication:** Required (ADMIN role in organization)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `job_title` | string | — | Filter by job title |
| `search` | string | — | Search by name or employee ID |
| `limit` | int | 50 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V70...",
      "user_id": "01HQ7V71...",
      "name": "Sarah Johnson",
      "employee_id": "EMP-001",
      "job_title": "Medical Assistant"
    }
  ],
  "total": 5,
  "limit": 50,
  "offset": 0
}
```

---

### `GET /api/organizations/{org_id}/staff/{staff_id}`
Get staff member details.

**Authentication:** Required (ADMIN or the staff member themselves)

**Response:**
```json
{
  "id": "01HQ7V70...",
  "user_id": "01HQ7V71...",
  "employee_id": "EMP-001",
  "job_title": "Medical Assistant",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### `POST /api/organizations/{org_id}/staff`
Create a staff profile for an existing member.

**Authentication:** Required (ADMIN role in organization)

**Request Body:**
```json
{
  "user_id": "01HQ7V71...",
  "employee_id": "EMP-001",
  "job_title": "Medical Assistant"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | ULID | Yes | User to associate |
| `employee_id` | string | No | Internal employee ID |
| `job_title` | string | Yes | Job title |

**Response:** `201 Created`
```json
{
  "id": "01HQ7V70...",
  "user_id": "01HQ7V71...",
  "employee_id": "EMP-001",
  "job_title": "Medical Assistant",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### `PATCH /api/organizations/{org_id}/staff/{staff_id}`
Update staff member details.

**Authentication:** Required (ADMIN role in organization)

**Request Body:**
```json
{
  "employee_id": "EMP-002",
  "job_title": "Senior Medical Assistant"
}
```

**Response:**
```json
{
  "id": "01HQ7V70...",
  "job_title": "Senior Medical Assistant",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### `DELETE /api/organizations/{org_id}/staff/{staff_id}`
Remove a staff profile (soft delete).

**Authentication:** Required (ADMIN role in organization)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |
| `staff_id` | ULID | Staff ID |

> [!CAUTION]
> This performs a soft delete. The staff member's data is retained for audit purposes but they lose access to the organization. Their user account remains active.

> [!NOTE]
> To completely remove a user from the organization, use `DELETE /api/organizations/{org_id}/members/{member_id}` instead.

**Response:**
```json
{
  "success": true,
  "deleted_at": "2024-01-15T10:40:00Z"
}
```

---

## Proxies & Patient Assignments

Manage proxy access to patient records (e.g., parents, guardians, POA).

**Related Endpoints:**
- [Patients](#patients) — Patient records
- [Consent](#consent--compliance) — Legal documentation

### `GET /api/users/me/proxy/patients`
Get patients managed by the current proxy user.

> [!WARNING]
> **Deprecated:** The legacy path `/api/proxies/me/patients` is deprecated and will be removed in a future release. Please migrate to `/api/users/me/proxy/patients`.

**Authentication:** Required (User with Proxy profile)

**Response:**
```json
{
  "items": [
    {
      "patient_id": "01HQ7V42...",
      "patient_name": "John Doe Jr.",
      "relationship_type": "PARENT",
      "permissions": {
        "can_view_clinical_notes": true,
        "can_view_billing": true,
        "can_schedule_appointments": true
      },
      "expires_at": null
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

### `GET /api/organizations/{org_id}/patients/{patient_id}/proxies`
List proxies assigned to a patient.

**Authentication:** Required (PROVIDER, STAFF, or ADMIN) 🔒

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V80...",
      "proxy_id": "01HQ7V41...",
      "proxy_name": "Jane Doe",
      "proxy_email": "jane@example.com",
      "relationship_type": "PARENT",
      "can_view_clinical_notes": true,
      "can_view_billing": true,
      "can_schedule_appointments": true,
      "expires_at": null,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### `POST /api/organizations/{org_id}/patients/{patient_id}/proxies`
Assign a proxy to a patient.

**Authentication:** Required (PROVIDER, STAFF, or ADMIN) 🔒

> [!IMPORTANT]
> This action triggers a `CREATE_ACCESS` audit log entry. The user must verify legal documentation (POA, Guardianship) before assigning.

**Request Body:**
```json
{
  "user_id": "01HQ7V46...",
  "relationship_type": "POA",
  "can_view_clinical_notes": true,
  "can_view_billing": true,
  "can_schedule_appointments": true,
  "expires_at": "2025-12-31T23:59:59Z"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | ULID | Yes | User to assign as proxy |
| `relationship_type` | string | Yes | `PARENT`, `GUARDIAN`, `POA`, `SPOUSE` |
| `can_view_clinical_notes` | boolean | No | Default: false |
| `can_view_billing` | boolean | No | Default: true |
| `can_schedule_appointments` | boolean | No | Default: true |
| `expires_at` | datetime | No | For temporary access |

**Response:** `201 Created`
```json
{
  "id": "01HQ7V80...",
  "proxy_id": "01HQ7V41...",
  "patient_id": "01HQ7V42...",
  "relationship_type": "POA",
  "permissions": {
    "can_view_clinical_notes": true,
    "can_view_billing": true,
    "can_schedule_appointments": true
  },
  "expires_at": "2025-12-31T23:59:59Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### `PATCH /api/organizations/{org_id}/patients/{patient_id}/proxies/{assignment_id}`
Update proxy permissions.

**Authentication:** Required (ADMIN only)

**Request Body:**
```json
{
  "can_view_clinical_notes": false,
  "expires_at": "2024-06-30T23:59:59Z"
}
```

**Response:**
```json
{
  "id": "01HQ7V80...",
  "can_view_clinical_notes": false,
  "expires_at": "2024-06-30T23:59:59Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### `DELETE /api/organizations/{org_id}/patients/{patient_id}/proxies/{assignment_id}`
Remove proxy access from a patient.

**Authentication:** Required (ADMIN only)

> [!WARNING]
> This immediately revokes all proxy access. The action is logged in audit logs.

**Response:**
```json
{
  "success": true,
  "revoked_at": "2024-01-15T10:40:00Z"
}
```

---

## Care Team

Manage provider assignments to patients.

**Related Endpoints:**
- [Patients](#patients) — Patient records
- [Providers](#providers) — Provider profiles

### `GET /api/organizations/{org_id}/patients/{patient_id}/care-team`
Get the care team for a patient.

**Authentication:** Required (PROVIDER, STAFF, patient self, or assigned Proxy) 🔒

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V47...",
      "provider_id": "01HQ7V44...",
      "provider_name": "Dr. Jane Smith",
      "specialty": "Internal Medicine",
      "is_primary": true,
      "assigned_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### `POST /api/organizations/{org_id}/patients/{patient_id}/care-team`
Add a provider to the care team.

**Authentication:** Required (ADMIN or existing Primary Provider)

**Request Body:**
```json
{
  "provider_id": "01HQ7V44...",
  "is_primary": false
}
```

**Response:** `201 Created`
```json
{
  "id": "01HQ7V47...",
  "provider_id": "01HQ7V44...",
  "patient_id": "01HQ7V42...",
  "is_primary": false,
  "assigned_at": "2024-01-15T10:30:00Z"
}
```

---

### `PATCH /api/organizations/{org_id}/patients/{patient_id}/care-team/{assignment_id}`
Update care team assignment (e.g., change primary status).

**Authentication:** Required (ADMIN or Primary Provider)

**Request Body:**
```json
{
  "is_primary": true
}
```

**Response:**
```json
{
  "id": "01HQ7V47...",
  "is_primary": true,
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### `DELETE /api/organizations/{org_id}/patients/{patient_id}/care-team/{assignment_id}`
Remove a provider from the care team.

**Authentication:** Required (ADMIN only)

**Response:**
```json
{
  "success": true,
  "removed_at": "2024-01-15T10:40:00Z"
}
```

---

## Appointments

Manage patient appointments and provider scheduling.

> [!IMPORTANT]
> All appointment endpoints involve Protected Health Information (PHI) and trigger audit log entries. 🔒

**Related Endpoints:**
- [Patients](#patients) — Patient records
- [Providers](#providers) — Provider profiles
- [Care Team](#care-team) — Provider-patient relationships

### `GET /api/organizations/{org_id}/appointments`
List appointments in an organization.

**Authentication:** Required (PROVIDER, STAFF, or ADMIN) 🔒

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `date` | date | — | Filter by specific date (YYYY-MM-DD) |
| `start_date` | date | — | Start of date range |
| `end_date` | date | — | End of date range |
| `status` | string | — | Filter: `SCHEDULED`, `CONFIRMED`, `COMPLETED`, `CANCELLED`, `NO_SHOW` |
| `patient_id` | ULID | — | Filter by patient |
| `provider_id` | ULID | — | Filter by provider |
| `limit` | int | 50 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V90...",
      "patient_id": "01HQ7V42...",
      "patient_name": "John Doe",
      "provider_id": "01HQ7V44...",
      "provider_name": "Dr. Jane Smith",
      "appointment_type": "IN_PERSON",
      "status": "SCHEDULED",
      "scheduled_at": "2024-01-20T14:00:00Z",
      "duration_minutes": 30,
      "reason": "Annual checkup",
      "location": "Room 101",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

---

### `GET /api/organizations/{org_id}/appointments/{appointment_id}`
Get appointment details.

**Authentication:** Required (Patient self, assigned Proxy, assigned Provider, or Staff) 🔒

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |
| `appointment_id` | ULID | Appointment ID |

**Response:**
```json
{
  "id": "01HQ7V90...",
  "patient_id": "01HQ7V42...",
  "patient_name": "John Doe",
  "provider_id": "01HQ7V44...",
  "provider_name": "Dr. Jane Smith",
  "appointment_type": "TELEHEALTH",
  "status": "CONFIRMED",
  "scheduled_at": "2024-01-20T14:00:00Z",
  "duration_minutes": 30,
  "reason": "Follow-up consultation",
  "notes": "Discuss lab results",
  "telehealth_url": "https://meet.lockdev.com/apt/01HQ7V90...",
  "telehealth_password": "123456",
  "reminders_sent": [
    {"type": "EMAIL", "sent_at": "2024-01-19T10:00:00Z"}
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T09:00:00Z"
}
```

---

### `POST /api/organizations/{org_id}/appointments`
Schedule a new appointment.

**Authentication:** Required (PROVIDER, STAFF, Patient self, or Proxy with `can_schedule_appointments`) 🔒

**Request Body:**
```json
{
  "patient_id": "01HQ7V42...",
  "provider_id": "01HQ7V44...",
  "appointment_type": "IN_PERSON",
  "scheduled_at": "2024-01-20T14:00:00Z",
  "duration_minutes": 30,
  "reason": "Annual checkup",
  "notes": "Patient requested early morning if possible",
  "location": "Room 101"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `patient_id` | ULID | Yes | Patient for the appointment |
| `provider_id` | ULID | Yes | Provider conducting the appointment |
| `appointment_type` | string | Yes | `IN_PERSON` or `TELEHEALTH` |
| `scheduled_at` | datetime | Yes | Appointment start time (ISO8601) |
| `duration_minutes` | int | No | Duration in minutes (default: 30) |
| `reason` | string | No | Reason for visit |
| `notes` | string | No | Additional notes |
| `location` | string | No | Room/location (for IN_PERSON) |

**Response:** `201 Created`
```json
{
  "id": "01HQ7V90...",
  "patient_id": "01HQ7V42...",
  "provider_id": "01HQ7V44...",
  "appointment_type": "IN_PERSON",
  "status": "SCHEDULED",
  "scheduled_at": "2024-01-20T14:00:00Z",
  "duration_minutes": 30,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Example curl:**
```bash
curl -X POST "https://api.lockdev.com/api/organizations/01HQ7V3Y.../appointments" \
  -H "Authorization: Bearer $FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: appt-$(uuidgen)" \
  -d '{
    "patient_id": "01HQ7V42...",
    "provider_id": "01HQ7V44...",
    "appointment_type": "IN_PERSON",
    "scheduled_at": "2024-01-20T14:00:00Z",
    "duration_minutes": 30,
    "reason": "Annual checkup"
  }'
```

---

### `PATCH /api/organizations/{org_id}/appointments/{appointment_id}`
Update or reschedule an appointment.

**Authentication:** Required (PROVIDER, STAFF, or ADMIN) 🔒

**Request Body:**
```json
{
  "status": "CONFIRMED",
  "scheduled_at": "2024-01-20T15:00:00Z",
  "notes": "Rescheduled per patient request"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `SCHEDULED`, `CONFIRMED`, `COMPLETED`, `CANCELLED`, `NO_SHOW` |
| `scheduled_at` | datetime | New appointment time |
| `duration_minutes` | int | Updated duration |
| `notes` | string | Updated notes |
| `cancellation_reason` | string | Required when status = `CANCELLED` |

**Response:**
```json
{
  "id": "01HQ7V90...",
  "status": "CONFIRMED",
  "scheduled_at": "2024-01-20T15:00:00Z",
  "updated_at": "2024-01-16T10:00:00Z"
}
```

---

### `DELETE /api/organizations/{org_id}/appointments/{appointment_id}`
Cancel an appointment.

**Authentication:** Required (PROVIDER, STAFF, ADMIN, Patient self, or Proxy) 🔒

**Request Body:**
```json
{
  "cancellation_reason": "Patient requested cancellation"
}
```

> [!NOTE]
> This is equivalent to `PATCH` with `status: CANCELLED`. The appointment record is retained for audit purposes.

**Response:**
```json
{
  "success": true,
  "status": "CANCELLED",
  "cancelled_at": "2024-01-16T10:00:00Z"
}
```

---

### `GET /api/organizations/{org_id}/providers/{provider_id}/availability`
Get available time slots for a provider.

**Authentication:** Required (Member of organization)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |
| `provider_id` | ULID | Provider ID |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start_date` | date | today | Start of availability window |
| `end_date` | date | +7 days | End of availability window |
| `duration_minutes` | int | 30 | Required slot duration |
| `appointment_type` | string | — | `IN_PERSON` or `TELEHEALTH` |

**Response:**
```json
{
  "provider_id": "01HQ7V44...",
  "provider_name": "Dr. Jane Smith",
  "availability": [
    {
      "date": "2024-01-20",
      "slots": [
        {"start": "09:00", "end": "09:30", "available": true},
        {"start": "09:30", "end": "10:00", "available": true},
        {"start": "10:00", "end": "10:30", "available": false},
        {"start": "10:30", "end": "11:00", "available": true}
      ]
    },
    {
      "date": "2024-01-21",
      "slots": [
        {"start": "14:00", "end": "14:30", "available": true},
        {"start": "14:30", "end": "15:00", "available": true}
      ]
    }
  ]
}
```

---

## Messaging

Secure messaging between patients and care teams.

> [!IMPORTANT]
> All messaging endpoints involve Protected Health Information (PHI) and trigger audit log entries. 🔒

**Related Endpoints:**
- [Patients](#patients) — Patient records
- [Care Team](#care-team) — Message recipients
- [Real-Time Events](#real-time-events-sse) — New message notifications

### `GET /api/organizations/{org_id}/messages`
List message threads for the current user.

**Authentication:** Required 🔒

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter` | string | — | `unread`, `archived` |
| `search` | string | — | Search in subject/content |
| `patient_id` | ULID | — | Filter by patient (Staff/Provider only) |
| `limit` | int | 50 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7VA0...",
      "subject": "Question about medication",
      "participants": [
        {"user_id": "01HQ7V42...", "name": "John Doe", "type": "PATIENT"},
        {"user_id": "01HQ7V44...", "name": "Dr. Jane Smith", "type": "PROVIDER"}
      ],
      "patient_id": "01HQ7V42...",
      "last_message": {
        "sender_name": "John Doe",
        "preview": "I have a question about my new prescription...",
        "sent_at": "2024-01-15T14:30:00Z"
      },
      "unread_count": 1,
      "is_archived": false,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T14:30:00Z"
    }
  ],
  "total": 15,
  "limit": 50,
  "offset": 0
}
```

---

### `POST /api/organizations/{org_id}/messages`
Start a new message thread.

**Authentication:** Required 🔒

**Request Body:**
```json
{
  "recipient_user_ids": ["01HQ7V44..."],
  "patient_id": "01HQ7V42...",
  "subject": "Question about medication",
  "body": "Hello Dr. Smith,\n\nI have a question about my new prescription. Is it safe to take with my current vitamins?\n\nThank you,\nJohn"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `recipient_user_ids` | array | Yes | User IDs to include in thread |
| `patient_id` | ULID | No | Associated patient (required for Staff/Provider) |
| `subject` | string | Yes | Message subject |
| `body` | string | Yes | Initial message content |

**Response:** `201 Created`
```json
{
  "id": "01HQ7VA0...",
  "subject": "Question about medication",
  "participants": [
    {"user_id": "01HQ7V42...", "name": "John Doe", "type": "PATIENT"},
    {"user_id": "01HQ7V44...", "name": "Dr. Jane Smith", "type": "PROVIDER"}
  ],
  "patient_id": "01HQ7V42...",
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

### `GET /api/organizations/{org_id}/messages/{thread_id}`
Get message thread with all messages.

**Authentication:** Required (Thread participant only) 🔒

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `org_id` | ULID | Organization ID |
| `thread_id` | ULID | Message thread ID |

**Response:**
```json
{
  "id": "01HQ7VA0...",
  "subject": "Question about medication",
  "participants": [
    {"user_id": "01HQ7V42...", "name": "John Doe", "type": "PATIENT"},
    {"user_id": "01HQ7V44...", "name": "Dr. Jane Smith", "type": "PROVIDER"}
  ],
  "patient_id": "01HQ7V42...",
  "messages": [
    {
      "id": "01HQ7VA1...",
      "sender_id": "01HQ7V42...",
      "sender_name": "John Doe",
      "body": "Hello Dr. Smith,\n\nI have a question about my new prescription...",
      "attachments": [],
      "sent_at": "2024-01-15T10:00:00Z",
      "read_by": [
        {"user_id": "01HQ7V42...", "read_at": "2024-01-15T10:00:00Z"},
        {"user_id": "01HQ7V44...", "read_at": "2024-01-15T14:00:00Z"}
      ]
    },
    {
      "id": "01HQ7VA2...",
      "sender_id": "01HQ7V44...",
      "sender_name": "Dr. Jane Smith",
      "body": "Hi John,\n\nYes, it is safe to take with your vitamins...",
      "attachments": [],
      "sent_at": "2024-01-15T14:30:00Z",
      "read_by": [
        {"user_id": "01HQ7V44...", "read_at": "2024-01-15T14:30:00Z"}
      ]
    }
  ],
  "is_archived": false,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T14:30:00Z"
}
```

---

### `POST /api/organizations/{org_id}/messages/{thread_id}/replies`
Reply to a message thread.

**Authentication:** Required (Thread participant only) 🔒

**Request Body:**
```json
{
  "body": "Thank you for the clarification, Dr. Smith!",
  "attachments": []
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `body` | string | Yes | Reply content |
| `attachments` | array | No | Document IDs to attach |

**Response:** `201 Created`
```json
{
  "id": "01HQ7VA3...",
  "thread_id": "01HQ7VA0...",
  "sender_id": "01HQ7V42...",
  "sender_name": "John Doe",
  "body": "Thank you for the clarification, Dr. Smith!",
  "attachments": [],
  "sent_at": "2024-01-15T16:00:00Z"
}
```

---

### `PATCH /api/organizations/{org_id}/messages/{thread_id}`
Update thread status (archive, mark read/unread).

**Authentication:** Required (Thread participant only) 🔒

**Request Body:**
```json
{
  "is_archived": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `is_archived` | boolean | Archive/unarchive thread |
| `mark_read` | boolean | Mark all messages as read |
| `mark_unread` | boolean | Mark thread as unread |

**Response:**
```json
{
  "id": "01HQ7VA0...",
  "is_archived": true,
  "updated_at": "2024-01-15T16:30:00Z"
}
```

---

## Call Center

Call center agent workspace and call management.

> [!IMPORTANT]
> Call center endpoints require the `CALL_CENTER_AGENT` role (a sub-type of Staff) with mandatory MFA. All access is logged. 🔒

**Related Endpoints:**
- [Patients](#patients) — Patient lookup
- [Appointments](#appointments) — Scheduling

### `GET /api/call-center/queue`
Get the current call queue.

**Authentication:** Required (CALL_CENTER_AGENT)

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7VB0...",
      "caller_id": "+1-555-123-4567",
      "patient_id": "01HQ7V42...",
      "patient_name": "John Doe",
      "wait_time_seconds": 45,
      "queue_position": 1,
      "call_type": "INBOUND",
      "entered_queue_at": "2024-01-15T10:29:15Z"
    }
  ],
  "total_in_queue": 3,
  "average_wait_time_seconds": 60
}
```

---

### `POST /api/call-center/queue/{queue_id}/accept`
Accept a call from the queue.

**Authentication:** Required (CALL_CENTER_AGENT)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `queue_id` | ULID | Queue entry ID |

**Response:**
```json
{
  "call_id": "01HQ7VB1...",
  "queue_id": "01HQ7VB0...",
  "caller_id": "+1-555-123-4567",
  "patient_id": "01HQ7V42...",
  "patient_name": "John Doe",
  "connected_at": "2024-01-15T10:30:00Z"
}
```

---

### `GET /api/call-center/calls/recent`
Get recent calls handled by the current agent.

**Authentication:** Required (CALL_CENTER_AGENT)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 20 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7VB1...",
      "caller_id": "+1-555-123-4567",
      "patient_id": "01HQ7V42...",
      "patient_name": "John Doe",
      "call_type": "INBOUND",
      "duration_seconds": 180,
      "outcome": "SCHEDULED_APPOINTMENT",
      "notes": "Scheduled annual checkup for next week",
      "started_at": "2024-01-15T10:30:00Z",
      "ended_at": "2024-01-15T10:33:00Z"
    }
  ],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

---

### `GET /api/call-center/calls/{call_id}`
Get call details.

**Authentication:** Required (CALL_CENTER_AGENT or ADMIN) 🔒

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `call_id` | ULID | Call ID |

**Response:**
```json
{
  "id": "01HQ7VB1...",
  "agent_id": "01HQ7V71...",
  "agent_name": "Sarah Johnson",
  "caller_id": "+1-555-123-4567",
  "patient_id": "01HQ7V42...",
  "patient_name": "John Doe",
  "call_type": "INBOUND",
  "duration_seconds": 180,
  "outcome": "SCHEDULED_APPOINTMENT",
  "notes": "Scheduled annual checkup for next week",
  "recording_available": true,
  "follow_up_tasks": [
    {
      "id": "01HQ7VB2...",
      "description": "Send appointment confirmation",
      "status": "COMPLETED"
    }
  ],
  "started_at": "2024-01-15T10:30:00Z",
  "ended_at": "2024-01-15T10:33:00Z"
}
```

---

### `PATCH /api/call-center/calls/{call_id}`
Update call notes and outcome.

**Authentication:** Required (CALL_CENTER_AGENT or ADMIN)

**Request Body:**
```json
{
  "outcome": "SCHEDULED_APPOINTMENT",
  "notes": "Scheduled annual checkup for January 20th at 2pm with Dr. Smith"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `outcome` | string | `RESOLVED`, `SCHEDULED_APPOINTMENT`, `TRANSFERRED`, `VOICEMAIL`, `CALLBACK_REQUESTED` |
| `notes` | string | Call notes |
| `patient_id` | ULID | Link call to a patient (if identified during call) |

**Response:**
```json
{
  "id": "01HQ7VB1...",
  "outcome": "SCHEDULED_APPOINTMENT",
  "notes": "Scheduled annual checkup for January 20th at 2pm with Dr. Smith",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### `GET /api/call-center/patients/{patient_id}/call-history`
Get call history for a specific patient.

**Authentication:** Required (CALL_CENTER_AGENT or ADMIN) 🔒

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `patient_id` | ULID | Patient ID |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 20 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "patient_id": "01HQ7V42...",
  "patient_name": "John Doe",
  "items": [
    {
      "id": "01HQ7VB1...",
      "agent_name": "Sarah Johnson",
      "call_type": "INBOUND",
      "duration_seconds": 180,
      "outcome": "SCHEDULED_APPOINTMENT",
      "started_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "01HQ7VB0...",
      "agent_name": "Mike Wilson",
      "call_type": "OUTBOUND",
      "duration_seconds": 90,
      "outcome": "CALLBACK_REQUESTED",
      "started_at": "2024-01-10T14:00:00Z"
    }
  ],
  "total": 8,
  "limit": 20,
  "offset": 0
}
```

---

### `POST /api/call-center/calls/{call_id}/tasks`
Create a follow-up task from a call.

**Authentication:** Required (CALL_CENTER_AGENT)

**Request Body:**
```json
{
  "description": "Follow up on lab results in 3 days",
  "due_at": "2024-01-18T10:00:00Z",
  "assignee_id": "01HQ7V71..."
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | Yes | Task description |
| `due_at` | datetime | No | Due date/time |
| `assignee_id` | ULID | No | Assigned agent (default: self) |

**Response:** `201 Created`
```json
{
  "id": "01HQ7VB3...",
  "call_id": "01HQ7VB1...",
  "description": "Follow up on lab results in 3 days",
  "status": "PENDING",
  "due_at": "2024-01-18T10:00:00Z",
  "assignee_id": "01HQ7V71...",
  "created_at": "2024-01-15T10:35:00Z"
}
```

---

### `GET /api/call-center/calls/{call_id}/recording-url`
Get a presigned URL to download the call recording.

**Authentication:** Required (CALL_CENTER_AGENT or ADMIN) 🔒

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `call_id` | ULID | Call ID |

> [!IMPORTANT]
> Call recordings contain PHI. Access is logged in audit logs, and URLs expire after 15 minutes.

**Response:**
```json
{
  "download_url": "https://s3.amazonaws.com/.../call-recording-01HQ7VB1...?...",
  "filename": "call-01HQ7VB1-2024-01-15.mp3",
  "duration_seconds": 180,
  "file_size_bytes": 2764800,
  "expires_at": "2024-01-15T10:50:00Z"
}
```

**Error Responses:**
| Code | Description |
|------|-------------|
| `RECORDING_NOT_AVAILABLE` | Recording not yet processed or retention expired |
| `RECORDING_REDACTED` | Recording has been redacted for compliance |

---

### `POST /api/call-center/calls/outbound`
Initiate an outbound call to a patient.

**Authentication:** Required (CALL_CENTER_AGENT) 🔒

> [!CAUTION]
> Before initiating outbound calls, the system checks the contact method's `is_safe_for_voicemail` flag and the patient's `communication_consent_transactional` status.

**Request Body:**
```json
{
  "patient_id": "01HQ7V42...",
  "contact_method_id": "01HQ7V43...",
  "reason": "Appointment reminder",
  "notes": "Following up on missed appointment"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `patient_id` | ULID | Yes | Patient to call |
| `contact_method_id` | ULID | Yes | Contact method to use |
| `reason` | string | Yes | Reason for call (logged) |
| `notes` | string | No | Pre-call notes |

**Response:** `201 Created`
```json
{
  "call_id": "01HQ7VB5...",
  "patient_id": "01HQ7V42...",
  "patient_name": "John Doe",
  "phone_number": "+1-555-123-4567",
  "call_type": "OUTBOUND",
  "status": "INITIATING",
  "initiated_at": "2024-01-15T10:35:00Z"
}
```

**Error Responses:**
| Code | Description |
|------|-------------|
| `VOICEMAIL_UNSAFE` | Contact is marked unsafe for calls |
| `CONSENT_NOT_GRANTED` | Patient has not consented to calls |
| `PATIENT_DISCHARGED` | Patient has been discharged |
| `CALL_LIMIT_EXCEEDED` | Too many call attempts today |

---

## Consent & Compliance

Manage legal consent documents and user agreements.

**Related Endpoints:**
- [Users](#users--authentication) — User profile
- [Communication Preferences](#get-apiusersmecommunication-preferences) — TCPA consent

### `GET /api/consent/required`
Get list of consent documents user must sign.

**Authentication:** Required

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V48...",
      "type": "HIPAA_NOTICE",
      "version": "v2.1",
      "title": "Notice of Privacy Practices",
      "content_url": "/api/consent/documents/01HQ7V48.../content"
    },
    {
      "id": "01HQ7V49...",
      "type": "TERMS_OF_SERVICE",
      "version": "v3.0",
      "title": "Terms of Service"
    }
  ],
  "total": 2
}
```

---

### `GET /api/consent/documents/{document_id}/content`
Get the full content of a consent document.

**Authentication:** Required

**Response:**
```json
{
  "id": "01HQ7V48...",
  "type": "HIPAA_NOTICE",
  "version": "v2.1",
  "title": "Notice of Privacy Practices",
  "content": "Full HTML or Markdown content of the document...",
  "effective_date": "2024-01-01"
}
```

---

### `POST /api/consent`
Record user consent for a document.

**Authentication:** Required

**Request Body:**
```json
{
  "document_id": "01HQ7V48...",
  "agreed": true
}
```

> [!NOTE]
> The server automatically records the IP address and timestamp.

**Response:**
```json
{
  "success": true,
  "signed_at": "2024-01-15T10:30:00Z"
}
```

---

### `GET /api/consent/history`
Get user's consent history.

**Authentication:** Required

**Response:**
```json
{
  "items": [
    {
      "document_type": "HIPAA_NOTICE",
      "document_version": "v2.1",
      "agreed_at": "2024-01-15T10:30:00Z",
      "ip_address": "192.168.1.1"
    }
  ]
}
```

---

## Documents

Secure document upload and management.

**Related Endpoints:**
- [Patients](#patients) — Patient records

### `POST /api/organizations/{org_id}/documents/upload-url`
Generate a presigned S3 URL for secure document upload.

**Authentication:** Required (PROVIDER, STAFF, or patient self) 🔒

**Request Body:**
```json
{
  "filename": "lab_results.pdf",
  "content_type": "application/pdf",
  "patient_id": "01HQ7V42..."
}
```

**Response:**
```json
{
  "upload_url": "https://s3.amazonaws.com/...",
  "document_id": "01HQ7V50...",
  "expires_at": "2024-01-15T11:30:00Z"
}
```

---

### `GET /api/organizations/{org_id}/patients/{patient_id}/documents`
List documents for a patient.

**Authentication:** Required (PROVIDER, STAFF, patient self, or assigned Proxy with `can_view_clinical_notes`) 🔒

> [!IMPORTANT]
> This endpoint triggers a `READ_ACCESS` audit log entry for HIPAA compliance.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `content_type` | string | — | Filter by MIME type |
| `limit` | int | 50 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V50...",
      "filename": "lab_results.pdf",
      "content_type": "application/pdf",
      "scan_status": "clean",
      "processing_status": "COMPLETED",
      "uploaded_at": "2024-01-15T10:30:00Z",
      "uploaded_by": "01HQ7V45..."
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

---

### `GET /api/organizations/{org_id}/documents/{document_id}`
Get document metadata and status.

**Authentication:** Required (appropriate permissions)

**Response:**
```json
{
  "id": "01HQ7V50...",
  "patient_id": "01HQ7V42...",
  "filename": "lab_results.pdf",
  "content_type": "application/pdf",
  "size_bytes": 245678,
  "scan_status": "clean",
  "processing_status": "COMPLETED",
  "extracted_text": "Lab results summary...",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "uploaded_by": "01HQ7V45...",
  "processed_at": "2024-01-15T10:31:00Z"
}
```

---

### `GET /api/organizations/{org_id}/documents/{document_id}/download-url`
Generate a presigned URL for secure document download.

**Authentication:** Required (appropriate permissions)

> [!IMPORTANT]
> This endpoint triggers a `DOWNLOAD_ACCESS` audit log entry for HIPAA compliance.

**Response:**
```json
{
  "download_url": "https://s3.amazonaws.com/...",
  "expires_at": "2024-01-15T11:30:00Z"
}
```

---

### `DELETE /api/organizations/{org_id}/documents/{document_id}`
Delete a document.

**Authentication:** Required (ADMIN only)

> [!CAUTION]
> This performs a soft delete. The file is retained in S3 for compliance but marked as deleted.

**Response:**
```json
{
  "success": true,
  "deleted_at": "2024-01-15T10:40:00Z"
}
```

---

## Billing & Subscriptions

Stripe-powered subscription management for organizations and patients.

**Related Endpoints:**
- [Organizations](#organizations-tenants) — Organization billing
- [Patients](#patients) — Patient billing

### Organization Billing

#### `POST /api/organizations/{org_id}/billing/checkout`
Create a Stripe Checkout Session for organization subscription.

**Authentication:** Required (ADMIN role in organization)

**Request Body:**
```json
{
  "price_id": "price_12345..."
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/...",
  "session_id": "cs_test_..."
}
```

---

#### `POST /api/organizations/{org_id}/billing/portal`
Create a Stripe Customer Portal session (manage subscription, invoices).

**Authentication:** Required (ADMIN role in organization)

**Response:**
```json
{
  "portal_url": "https://billing.stripe.com/p/login/..."
}
```

---

### Patient Billing

#### `POST /api/organizations/{org_id}/patients/{patient_id}/billing/checkout`
Create checkout session for Patient subscription.

**Authentication:** Required (Patient Self or Proxy with `can_view_billing`)

**Request Body:**
```json
{
  "price_id": "price_patient_tier..."
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/...",
  "session_id": "cs_test_..."
}
```

---

#### `POST /api/organizations/{org_id}/patients/{patient_id}/billing/portal`
Manage Patient subscription.

**Authentication:** Required (Patient Self or Proxy with `can_view_billing`)

**Response:**
```json
{
  "portal_url": "https://billing.stripe.com/p/login/..."
}
```

---

## Real-Time Events (SSE)

Server-Sent Events for real-time notifications and updates.

> [!NOTE]
> SSE provides a long-lived HTTP connection for server-to-client push notifications. This is the primary mechanism for real-time updates in the frontend.

**Related Endpoints:**
- [Notifications](#notifications) — Notification management
- [Messaging](#messaging) — Message delivery

### `GET /api/events`
Server-Sent Events stream for real-time updates.

**Authentication:** Required (Bearer token as query parameter or header)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `token` | string | — | Alternative to Authorization header (for EventSource API) |

**Event Types:**
| Event | Description | Payload |
|-------|-------------|---------|
| `notification.new` | New notification created | `{ notification_id, type, title, body }` |
| `message.new` | New message in subscribed thread | `{ thread_id, sender_name, preview }` |
| `appointment.reminder` | Upcoming appointment reminder | `{ appointment_id, scheduled_at, provider_name }` |
| `appointment.updated` | Appointment rescheduled/cancelled | `{ appointment_id, status, scheduled_at }` |
| `document.processed` | Document finished OCR/virus scan | `{ document_id, status, patient_id }` |
| `document.scan_complete` | Virus scan completed | `{ document_id, scan_status }` |
| `consent.required` | New consent document available | `{ document_type, document_version }` |
| `call.incoming` | Incoming call (Call Center) | `{ call_id, caller_id, patient_id }` |
| `call.completed` | Call ended | `{ call_id, duration, outcome }` |
| `impersonation.started` | Admin started impersonating | `{ patient_id, expires_at }` |
| `impersonation.ended` | Impersonation session ended | `{ patient_id, reason }` |
| `heartbeat` | Keep-alive (every 30 seconds) | `{ timestamp }` |

**Example Event Stream:**
```
event: notification.new
data: {"notification_id": "01HQ7VC0...", "type": "message", "title": "New Message", "body": "Dr. Smith replied..."}

event: heartbeat
data: {"timestamp": "2024-01-15T10:30:00Z"}

event: message.new
data: {"thread_id": "01HQ7VA0...", "sender_name": "Dr. Jane Smith", "preview": "Your test results are..."}
```

**Connection Handling:**

```javascript
// Recommended: Using fetch-event-source for auth support
import { fetchEventSource } from '@microsoft/fetch-event-source';

await fetchEventSource('/api/events', {
  headers: {
    'Authorization': `Bearer ${token}`,
  },
  onmessage(event) {
    const data = JSON.parse(event.data);
    switch(event.event) {
      case 'notification.new':
        showNotification(data);
        break;
      case 'message.new':
        refreshMessageThread(data.thread_id);
        break;
    }
  },
  onerror(err) {
    console.error('SSE connection error:', err);
    // Automatic reconnection with exponential backoff
  },
});
```

**Reconnection Behavior:**
| Scenario | Response | Client Behavior |
|----------|----------|-----------------|
| Network disconnect | Connection lost | Auto-retry with exponential backoff (1s, 2s, 4s, max 30s) |
| Token expired | 401 Unauthorized | Refresh token, then reconnect |
| Server restart | Connection lost | Auto-retry, server sends full state on reconnect |
| Rate limited | 429 Too Many Requests | Wait for `Retry-After` header duration |

**SSE Status Indicator (Frontend):**
- 🟢 Green dot = Connected, receiving heartbeats
- 🟡 Yellow dot = Reconnecting
- 🔴 Red dot = Offline (>60s without heartbeat)

---

### `GET /api/organizations/{org_id}/events`
Organization-scoped SSE stream (for admin views).

**Authentication:** Required (ADMIN or SUPER_ADMIN)

**Event Types (in addition to user events):**
| Event | Description |
|-------|-------------|
| `member.joined` | New member accepted invitation |
| `member.removed` | Member removed from organization |
| `subscription.updated` | Subscription status changed |
| `license.expiring` | Provider license expiring soon |

---

## Admin Endpoints

> [!WARNING]
> Admin endpoints require `ADMIN` role and MFA. All actions are logged for audit purposes.

**Related Endpoints:**
- [Organization Members](#organization-members) — Member management

### `POST /api/admin/impersonate/{patient_id}`
Generate an impersonation token for patient support.

**Authentication:** Required (ADMIN with MFA)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `patient_id` | ULID | Patient to impersonate |

**Request Body:**
```json
{
  "reason": "Patient requested help resetting preferences"
}
```

> [!CAUTION]
> A "Break Glass" audit log entry is created BEFORE the token is generated. This is an auditable action.

**Response:**
```json
{
  "custom_token": "eyJhbGciOiJSUzI1NiIs...",
  "expires_in": 3600,
  "audit_log_id": "01HQ7V51..."
}
```

---

### `GET /api/admin/audit-logs`
Query audit logs.

**Authentication:** Required (ADMIN or SUPER_ADMIN)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `actor_user_id` | ULID | — | Filter by actor |
| `resource_type` | string | — | Filter: `PATIENT`, `DOCUMENT`, etc. |
| `action_type` | string | — | Filter: `READ`, `CREATE`, `UPDATE`, `DELETE` |
| `start_date` | ISO8601 | — | Start of date range |
| `end_date` | ISO8601 | — | End of date range |
| `limit` | int | 100 | Max results (max: 1000) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V52...",
      "actor_user_id": "01HQ7V45...",
      "actor_email": "admin@example.com",
      "organization_id": "01HQ7V3Y...",
      "resource_type": "PATIENT",
      "resource_id": "01HQ7V42...",
      "action_type": "READ",
      "ip_address": "192.168.1.1",
      "occurred_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 5000,
  "limit": 100,
  "offset": 0
}
```

---

### `GET /api/admin/audit-logs/export`
Export audit logs as CSV.

**Authentication:** Required (ADMIN or SUPER_ADMIN)

**Query Parameters:** Same as `GET /api/admin/audit-logs`

**Response:** `200 OK` with `Content-Type: text/csv`

---

## Super Admin Endpoints

> [!CAUTION]
> Super Admin endpoints provide platform-wide access. All actions are heavily audited. These endpoints require `SUPER_ADMIN` role.

**Related Endpoints:**
- [Admin Endpoints](#admin-endpoints) — Organization-level admin
- [Organizations](#organizations-tenants) — Organization management

### `GET /api/super-admin/organizations`
List all organizations on the platform.

**Authentication:** Required (SUPER_ADMIN)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | — | Search by name or ID |
| `status` | string | — | Filter: `ACTIVE`, `SUSPENDED`, `DELETED` |
| `subscription_status` | string | — | Filter: `ACTIVE`, `PAST_DUE`, `CANCELED` |
| `limit` | int | 50 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V3Y...",
      "name": "ACME Clinic",
      "status": "ACTIVE",
      "subscription_status": "ACTIVE",
      "member_count": 25,
      "patient_count": 1250,
      "created_at": "2024-01-01T00:00:00Z",
      "last_activity_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

---

### `GET /api/super-admin/users`
List all users across all organizations.

**Authentication:** Required (SUPER_ADMIN) 🔒

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | — | Search by email or name |
| `status` | string | — | Filter: `ACTIVE`, `LOCKED`, `SUSPENDED` |
| `mfa_enabled` | boolean | — | Filter by MFA status |
| `limit` | int | 50 | Max results (max: 100) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V3X...",
      "email": "user@example.com",
      "display_name": "John Doe",
      "status": "ACTIVE",
      "mfa_enabled": true,
      "organizations": [
        {"id": "01HQ7V3Y...", "name": "ACME Clinic", "role": "PROVIDER"}
      ],
      "last_login_at": "2024-01-15T10:00:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 5000,
  "limit": 50,
  "offset": 0
}
```

---

### `GET /api/super-admin/users/{user_id}`
Get detailed user information.

**Authentication:** Required (SUPER_ADMIN) 🔒

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | ULID | User ID |

**Response:**
```json
{
  "id": "01HQ7V3X...",
  "email": "user@example.com",
  "display_name": "John Doe",
  "status": "LOCKED",
  "mfa_enabled": true,
  "lockout_info": {
    "failed_attempts": 5,
    "locked_at": "2024-01-15T10:20:00Z",
    "unlock_at": "2024-01-15T10:35:00Z",
    "reason": "FAILED_LOGIN_ATTEMPTS"
  },
  "organizations": [
    {"id": "01HQ7V3Y...", "name": "ACME Clinic", "role": "PROVIDER"}
  ],
  "sessions": [
    {"id": "01HQ7V53...", "device": "Chrome on macOS", "last_active_at": "2024-01-15T10:15:00Z"}
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### `POST /api/super-admin/users/{user_id}/unlock`
Unlock a locked user account.

**Authentication:** Required (SUPER_ADMIN)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | ULID | User ID to unlock |

**Request Body:**
```json
{
  "reason": "User contacted support and verified identity"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reason` | string | Yes | Reason for unlock (min 10 characters, audit logged) |

> [!IMPORTANT]
> This action is logged in audit logs with the reason provided.

**Response:**
```json
{
  "success": true,
  "unlocked_at": "2024-01-15T10:40:00Z",
  "audit_log_id": "01HQ7V56..."
}
```

---

### `POST /api/super-admin/users/{user_id}/suspend`
Suspend a user account.

**Authentication:** Required (SUPER_ADMIN)

**Request Body:**
```json
{
  "reason": "Suspected unauthorized access"
}
```

**Response:**
```json
{
  "success": true,
  "suspended_at": "2024-01-15T10:40:00Z",
  "audit_log_id": "01HQ7V57..."
}
```

---

### `POST /api/super-admin/users/{user_id}/force-password-reset`
Force a password reset for a user.

**Authentication:** Required (SUPER_ADMIN)

**Request Body:**
```json
{
  "reason": "New employee onboarding - setting initial password"
}
```

> [!NOTE]
> This invalidates all user sessions and sends a password reset email.

**Response:**
```json
{
  "success": true,
  "email_sent_at": "2024-01-15T10:40:00Z",
  "sessions_terminated": 2
}
```

---

### `GET /api/super-admin/system/health`
Get detailed system health information.

**Authentication:** Required (SUPER_ADMIN)

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "api": {"status": "ok", "latency_ms": 12},
    "database": {"status": "ok", "pool_usage": "15/50"},
    "redis": {"status": "ok", "memory_usage": "45%"},
    "s3": {"status": "ok"},
    "ses": {"status": "ok", "quota_remaining": 45000}
  },
  "background_jobs": {
    "queue_depth": 42,
    "failed_last_hour": 3,
    "workers_active": 4
  },
  "checked_at": "2024-01-15T10:30:00Z"
}
```

---

### `GET /api/super-admin/system/metrics`
Get platform performance metrics.

**Authentication:** Required (SUPER_ADMIN)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | string | `1h` | Time period: `15m`, `1h`, `24h`, `7d` |

**Response:**
```json
{
  "period": "1h",
  "requests": {
    "total": 15420,
    "per_minute_avg": 257,
    "error_rate_percent": 0.12
  },
  "latency": {
    "p50_ms": 45,
    "p95_ms": 180,
    "p99_ms": 350
  },
  "active_users": 245,
  "active_sessions": 312
}
```

---

## Support

User support ticket management.

> [!NOTE]
> Support tickets are created by authenticated users and routed to the appropriate support team.

**Related Endpoints:**
- [Users & Authentication](#users--authentication) — User identity

### `POST /api/support/tickets`
Create a new support ticket.

**Authentication:** Required

**Request Body:**
```json
{
  "category": "TECHNICAL",
  "subject": "Cannot upload documents",
  "body": "When I try to upload a PDF, I get an error message...",
  "urgency": "NORMAL",
  "screenshot_document_id": "01HQ7V58..."
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category` | string | Yes | `TECHNICAL`, `BILLING`, `CLINICAL`, `ACCOUNT`, `OTHER` |
| `subject` | string | Yes | Brief description (max 200 chars) |
| `body` | string | Yes | Detailed description |
| `urgency` | string | No | `LOW`, `NORMAL` (default), `HIGH`, `URGENT` |
| `screenshot_document_id` | ULID | No | Uploaded screenshot document ID |

> [!NOTE]
> The ticket automatically captures the user's ID, email, organization context, and browser information for troubleshooting.

**Response:** `201 Created`
```json
{
  "id": "01HQ7V59...",
  "ticket_number": "TKT-2024-00123",
  "category": "TECHNICAL",
  "subject": "Cannot upload documents",
  "status": "OPEN",
  "created_at": "2024-01-15T10:30:00Z",
  "estimated_response": "Within 24 hours"
}
```

---

### `GET /api/support/tickets`
List user's support tickets.

**Authentication:** Required

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | — | Filter: `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` |
| `limit` | int | 20 | Max results (max: 50) |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "01HQ7V59...",
      "ticket_number": "TKT-2024-00123",
      "category": "TECHNICAL",
      "subject": "Cannot upload documents",
      "status": "IN_PROGRESS",
      "last_update_at": "2024-01-15T14:00:00Z",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 3,
  "limit": 20,
  "offset": 0
}
```

---

### `GET /api/support/tickets/{ticket_id}`
Get ticket details and conversation history.

**Authentication:** Required (ticket owner only)

**Response:**
```json
{
  "id": "01HQ7V59...",
  "ticket_number": "TKT-2024-00123",
  "category": "TECHNICAL",
  "subject": "Cannot upload documents",
  "body": "When I try to upload a PDF...",
  "status": "IN_PROGRESS",
  "urgency": "NORMAL",
  "messages": [
    {
      "id": "01HQ7V5A...",
      "sender": "user",
      "body": "When I try to upload a PDF...",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "01HQ7V5B...",
      "sender": "support",
      "sender_name": "Support Team",
      "body": "Thank you for contacting us. Could you please...",
      "created_at": "2024-01-15T14:00:00Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### `POST /api/support/tickets/{ticket_id}/messages`
Add a message to an existing ticket.

**Authentication:** Required (ticket owner only)

**Request Body:**
```json
{
  "body": "I tried that and it still doesn't work. Here's another screenshot...",
  "attachment_document_id": "01HQ7V5C..."
}
```

**Response:**
```json
{
  "id": "01HQ7V5D...",
  "sender": "user",
  "body": "I tried that and it still doesn't work...",
  "created_at": "2024-01-15T15:00:00Z"
}
```

---

## Analytics

### `POST /api/telemetry`
Log a user behavioral event.

**Authentication:** Required

**Request Body:**
```json
{
  "event_name": "onboarding_completed",
  "properties": {
    "step": 4,
    "skipped_tutorial": false
  }
}
```

**Response:**
```json
{
  "status": "ok"
}
```

---

## Analytics

### `POST /api/telemetry`
Log a user behavioral event.

**Authentication:** Required

**Request Body:**
```json
{
  "event_name": "onboarding_completed",
  "properties": {
    "step": 4,
    "skipped_tutorial": false
  }
}
```

**Response:**
```json
{
  "status": "ok"
}
```

---

## Webhooks

External service webhook endpoints.

### `POST /api/webhooks/stripe`
Handle Stripe webhook events.

**Authentication:** Stripe signature verification (no JWT)

**Headers:**
```
Stripe-Signature: t=1234567890,v1=...
```

**Events Handled:**
| Event | Action |
|-------|--------|
| `checkout.session.completed` | Activate subscription |
| `invoice.payment_succeeded` | Update payment status |
| `invoice.payment_failed` | Mark subscription past_due |
| `customer.subscription.updated` | Sync subscription status |
| `customer.subscription.deleted` | Cancel subscription |

**Response:**
```json
{
  "received": true
}
```

> [!NOTE]
> Webhook signature verification is performed using `stripe.Webhook.construct_event()`. Invalid signatures return 400.

---

## AI Services

AI-powered features using Google Vertex AI (Gemini).

### `POST /api/organizations/{org_id}/ai/summarize`
Generate an AI summary of text (e.g., clinical notes).

**Authentication:** Required (PROVIDER only)

**Request Body:**
```json
{
  "text": "Patient presents with...",
  "max_length": 150
}
```

**Response:**
```json
{
  "summary": "55-year-old male presenting with...",
  "model": "gemini-1.5-pro",
  "tokens_used": 245
}
```

> [!IMPORTANT]
> All AI requests are processed with Zero Data Retention settings enabled. No PHI is stored by the AI provider.

---

## Appendix: ID Formats

All resource IDs use **ULID** (Universally Unique Lexicographically Sortable Identifier):

```
01HQ7V3XK2QJPN8WMJK0ABCD12
└────┬────┘└───────┬────────┘
  Timestamp      Randomness
  (48 bits)      (80 bits)
```

**Benefits:**
- Lexicographically sortable (newest first in index scans)
- Non-enumerable (prevents ID guessing attacks)
- URL-safe (no special characters)

**Example Usage:**
```bash
# Valid ULID
01HQ7V3XK2QJPN8WMJK0ABCD12

# In API calls
GET /api/organizations/01HQ7V3Y.../patients/01HQ7V42...
```

---

## Appendix: PHI Access Matrix

Endpoints that access Protected Health Information (PHI) are marked with 🔒 throughout this document. The following matrix provides a complete reference:

| Endpoint Pattern | PHI Access | Audit Logged |
|-----------------|:----------:|:------------:|
| `/api/organizations/{org_id}/patients*` | 🔒 | ✓ |
| `/api/organizations/{org_id}/appointments*` | 🔒 | ✓ |
| `/api/organizations/{org_id}/messages*` | 🔒 | ✓ |
| `/api/organizations/{org_id}/documents*` | 🔒 | ✓ |
| `/api/organizations/{org_id}/patients/{patient_id}/contact-methods*` | 🔒 | ✓ |
| `/api/organizations/{org_id}/patients/{patient_id}/care-team*` | 🔒 | ✓ |
| `/api/organizations/{org_id}/patients/{patient_id}/proxies*` | 🔒 | ✓ |
| `/api/organizations/{org_id}/patients/{patient_id}/enrollment*` | 🔒 | ✓ |
| `/api/patients/{patient_id}/organizations` | 🔒 | ✓ |
| `/api/users/me/proxy/patients` | 🔒 | ✓ |
| `/api/call-center/*` | 🔒 | ✓ |
| `/api/admin/impersonate/{patient_id}` | 🔒 | ✓ (Break Glass) |
| `/api/admin/audit-logs*` | 🔒 (Masked) | ✓ |
| `/api/organizations/{org_id}/ai/summarize` | 🔒 | ✓ |

### PHI Data Elements

The following data elements are considered PHI under HIPAA:

- Patient names
- Dates (birth, death, admission, discharge, service)
- Geographic data (smaller than state)
- Phone/fax numbers
- Email addresses
- Social Security numbers
- Medical record numbers
- Health plan beneficiary numbers
- Account numbers
- Certificate/license numbers
- Vehicle identifiers
- Device identifiers/serial numbers
- URLs and IP addresses
- Biometric identifiers
- Full-face photographs
- Any other unique identifying characteristic

---

## Appendix: Audit Log Triggers

The following actions automatically trigger audit log entries for HIPAA compliance:

### Patient Access

| Endpoint | Action Type | Resource Type |
|----------|-------------|---------------|
| `GET /api/.../patients/{id}` | `READ` | `PATIENT` |
| `POST /api/.../patients` | `CREATE` | `PATIENT` |
| `PATCH /api/.../patients/{id}` | `UPDATE` | `PATIENT` |
| `DELETE /api/.../patients/{id}` | `DELETE` | `PATIENT` |

### Document Access

| Endpoint | Action Type | Resource Type |
|----------|-------------|---------------|
| `GET /api/.../documents` | `LIST` | `DOCUMENT` |
| `GET /api/.../documents/{id}` | `READ` | `DOCUMENT` |
| `GET /api/.../documents/{id}/download-url` | `DOWNLOAD` | `DOCUMENT` |
| `POST /api/.../documents/upload-url` | `CREATE` | `DOCUMENT` |
| `DELETE /api/.../documents/{id}` | `DELETE` | `DOCUMENT` |

### Appointment Access

| Endpoint | Action Type | Resource Type |
|----------|-------------|---------------|
| `GET /api/.../appointments/{id}` | `READ` | `APPOINTMENT` |
| `POST /api/.../appointments` | `CREATE` | `APPOINTMENT` |
| `PATCH /api/.../appointments/{id}` | `UPDATE` | `APPOINTMENT` |
| `DELETE /api/.../appointments/{id}` | `CANCEL` | `APPOINTMENT` |

### Messaging Access

| Endpoint | Action Type | Resource Type |
|----------|-------------|---------------|
| `GET /api/.../messages/{id}` | `READ` | `MESSAGE_THREAD` |
| `POST /api/.../messages` | `CREATE` | `MESSAGE_THREAD` |
| `POST /api/.../messages/{id}/replies` | `CREATE` | `MESSAGE` |

### Proxy/Access Management

| Endpoint | Action Type | Resource Type |
|----------|-------------|---------------|
| `POST /api/.../patients/{id}/proxies` | `GRANT_ACCESS` | `PROXY_ASSIGNMENT` |
| `PATCH /api/.../patients/{id}/proxies/{id}` | `UPDATE_ACCESS` | `PROXY_ASSIGNMENT` |
| `DELETE /api/.../patients/{id}/proxies/{id}` | `REVOKE_ACCESS` | `PROXY_ASSIGNMENT` |

### Administrative Actions

| Endpoint | Action Type | Resource Type |
|----------|-------------|---------------|
| `POST /api/admin/impersonate/{id}` | `BREAK_GLASS` | `IMPERSONATION` |
| `GET /api/admin/audit-logs` | `READ` | `AUDIT_LOG` |
| `GET /api/admin/audit-logs/export` | `EXPORT` | `AUDIT_LOG` |

### Audit Log Entry Structure

```json
{
  "id": "01HQ7V52...",
  "actor_user_id": "01HQ7V45...",
  "actor_email": "admin@example.com",
  "organization_id": "01HQ7V3Y...",
  "resource_type": "PATIENT",
  "resource_id": "01HQ7V42...",
  "action_type": "READ",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0 ...",
  "impersonator_id": null,
  "changes_json": null,
  "occurred_at": "2024-01-15T10:30:00Z"
}
```

> [!IMPORTANT]
> Audit logs are **immutable**. Rows in the `audit_logs` table are never deleted or modified. This is a HIPAA requirement for maintaining a complete access history.

---

## Appendix: OpenAPI Specification

An auto-generated OpenAPI 3.1 specification is available at runtime:

| Format | URL | Description |
|--------|-----|-------------|
| Swagger UI | `/docs` | Interactive API explorer |
| ReDoc | `/redoc` | Clean, readable documentation |
| Raw JSON | `/openapi.json` | Machine-readable specification |

### Using the OpenAPI Spec

**Import into Postman:**
1. Open Postman → Import → Link
2. Enter: `https://api.lockdev.com/openapi.json`
3. Click Import

**Generate Client SDKs:**
```bash
# TypeScript/JavaScript
npx openapi-typescript https://api.lockdev.com/openapi.json -o src/lib/api-types.d.ts

# Python
pip install openapi-python-client
openapi-python-client generate --url https://api.lockdev.com/openapi.json

# Go
go install github.com/deepmap/oapi-codegen/v2/cmd/oapi-codegen@latest
oapi-codegen -package api https://api.lockdev.com/openapi.json > api/client.go
```

### Spec Validation

The OpenAPI specification is validated on every CI build. To validate locally:

```bash
# Using Spectral
npx @stoplight/spectral-cli lint backend/openapi.json

# Using OpenAPI Validator
npx swagger-cli validate backend/openapi.json
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.2.0 | 2024-12-30 | **Security & Platform Enhancements:** Added: Super Admin Endpoints (`/api/super-admin/*`) for platform-wide administration. Added: Support Tickets API (`/api/support/tickets`). Enhanced: Real-Time Events (SSE) with complete event type documentation, reconnection behavior, and organization-scoped streams. Added: User account lockout/unlock endpoints. Added: System health and metrics endpoints. |
| 2.1.0 | 2024-12-30 | **Documentation Enhancement:** Added: API Versioning section. Added: Request Tracing (X-Request-ID). Added: Idempotency support documentation. Added: OpenAPI Specification appendix. Added: Complete curl examples. Added: Domain-specific error codes. Added: Missing endpoints (GET/POST/DELETE invitations, DELETE providers, DELETE staff, call recording-url, outbound calls). Fixed: Deprecated legacy `/api/proxies/me/patients` path with migration guidance. |
| 2.0.0 | 2024-12-30 | **Major Update:** Added: User Sessions, MFA, Invitations, Contact Methods, Organization-Patient Relationships, Appointments, Messaging, Call Center modules. Added: POST /api/organizations (create). Added: PHI Access Matrix and Audit Log Triggers appendices. Enhanced: PHI indicators (🔒) throughout. Fixed: Pagination consistency across all list endpoints. |
| 1.1.0 | 2024-12-30 | Added: Organization Members, Staff, Webhooks, User Profile. Fixed: Path consistency. Added: Cross-references. |
| 1.0.0 | 2024-12-30 | Initial API Reference |
