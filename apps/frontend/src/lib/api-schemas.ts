import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

const ImpersonationRequest = z.object({ reason: z.string() }).passthrough();
const ValidationError = z
  .object({
    loc: z.array(z.union([z.string(), z.number()])),
    msg: z.string(),
    type: z.string(),
  })
  .passthrough();
const HTTPValidationError = z
  .object({ detail: z.array(ValidationError) })
  .partial()
  .passthrough();
const ConsentSignRequest = z.object({ document_id: z.string() }).passthrough();
const UserRead = z
  .object({
    id: z.string().uuid(),
    email: z.string().email(),
    display_name: z.union([z.string(), z.null()]).optional(),
    is_super_admin: z.boolean().optional().default(false),
    mfa_enabled: z.boolean().optional().default(false),
    requires_consent: z.boolean().optional().default(true),
    transactional_consent: z.boolean().optional().default(true),
    marketing_consent: z.boolean().optional().default(false),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
const UserDeleteRequest = z
  .object({
    password: z.string().min(1),
    reason: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const UserDeleteResponse = z
  .object({
    success: z.boolean().optional().default(true),
    deleted_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
const UserUpdate = z
  .object({ display_name: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const SessionRead = z
  .object({
    id: z.string().uuid(),
    device: z.string(),
    ip_address: z.union([z.string(), z.null()]).optional(),
    location: z.union([z.string(), z.null()]).optional(),
    is_current: z.boolean().optional().default(false),
    created_at: z.string().datetime({ offset: true }),
    last_active_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
const SessionListResponse = z
  .object({
    items: z.array(SessionRead),
    total: z.number().int(),
    limit: z.number().int().optional().default(50),
    offset: z.number().int().optional().default(0),
  })
  .passthrough();
const SessionRevokeResponse = z
  .object({
    success: z.boolean().optional().default(true),
    terminated_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
const UserExportRequest = z
  .object({
    format: z
      .string()
      .regex(/^(json|pdf)$/)
      .default("json"),
    include_documents: z.boolean().default(false),
  })
  .partial()
  .passthrough();
const UserExportResponse = z
  .object({
    export_id: z.string().uuid(),
    status: z.string().optional().default("PENDING"),
    estimated_completion: z.string().datetime({ offset: true }),
  })
  .passthrough();
const CommunicationPreferencesRead = z
  .object({
    transactional_consent: z.boolean(),
    marketing_consent: z.boolean(),
    updated_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
const CommunicationPreferencesUpdate = z
  .object({
    transactional_consent: z.union([z.boolean(), z.null()]),
    marketing_consent: z.union([z.boolean(), z.null()]),
  })
  .partial()
  .passthrough();
const MFASetupResponse = z
  .object({
    secret: z.string(),
    provisioning_uri: z.string(),
    qr_code_data_url: z.union([z.string(), z.null()]).optional(),
    expires_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
const MFAVerifyRequest = z
  .object({
    code: z
      .string()
      .min(6)
      .max(6)
      .regex(/^[0-9]{6}$/),
  })
  .passthrough();
const MFAVerifyResponse = z
  .object({
    success: z.boolean().optional().default(true),
    mfa_enabled: z.boolean().optional().default(true),
    backup_codes: z.array(z.string()),
    enabled_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
const MFADisableRequest = z
  .object({ password: z.string().min(1) })
  .passthrough();
const MFADisableResponse = z
  .object({
    success: z.boolean().optional().default(true),
    mfa_enabled: z.boolean().optional().default(false),
    disabled_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
const DeviceTokenRequest = z
  .object({
    token: z.string().min(1).max(512),
    platform: z.string().regex(/^(ios|android|web)$/),
    device_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const DeviceTokenResponse = z
  .object({ success: z.boolean().default(true) })
  .partial()
  .passthrough();
const DeviceTokenDeleteRequest = z
  .object({ token: z.string().min(1).max(512) })
  .passthrough();
const OrganizationRead = z
  .object({
    name: z.string().max(255),
    tax_id: z.union([z.string(), z.null()]).optional(),
    settings_json: z.object({}).partial().passthrough().optional(),
    id: z.string().uuid(),
    stripe_customer_id: z.union([z.string(), z.null()]),
    subscription_status: z.string(),
    is_active: z.boolean(),
    member_count: z.number().int(),
    patient_count: z.number().int(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
const OrganizationCreate = z
  .object({
    name: z.string().max(255),
    tax_id: z.union([z.string(), z.null()]).optional(),
    settings_json: z.object({}).partial().passthrough().optional(),
  })
  .passthrough();
const OrganizationUpdate = z
  .object({
    name: z.union([z.string(), z.null()]),
    tax_id: z.union([z.string(), z.null()]),
    settings_json: z.union([z.object({}).partial().passthrough(), z.null()]),
  })
  .partial()
  .passthrough();
const MemberRead = z
  .object({
    id: z.string().uuid(),
    user_id: z.string().uuid(),
    organization_id: z.string().uuid(),
    email: z.union([z.string(), z.null()]).optional(),
    display_name: z.union([z.string(), z.null()]).optional(),
    role: z.string(),
    created_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
const InvitationCreate = z
  .object({ email: z.string().email(), role: z.string() })
  .passthrough();
const InvitationRead = z
  .object({
    email: z.string().email(),
    role: z.string(),
    id: z.string().uuid(),
    token: z.string(),
    status: z.string(),
    organization_id: z.string().uuid(),
    invited_by_user_id: z.string().uuid(),
    created_at: z.string().datetime({ offset: true }),
    expires_at: z.string().datetime({ offset: true }),
    accepted_at: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const token = z.union([z.string(), z.null()]).optional();
const TelemetryEvent = z
  .object({
    event_name: z.string().min(1).max(100),
    properties: z.object({}).partial().passthrough().optional(),
  })
  .passthrough();
const TelemetryResponse = z
  .object({
    success: z.boolean().default(true),
    event_id: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();

export const schemas = {
  ImpersonationRequest,
  ValidationError,
  HTTPValidationError,
  ConsentSignRequest,
  UserRead,
  UserDeleteRequest,
  UserDeleteResponse,
  UserUpdate,
  SessionRead,
  SessionListResponse,
  SessionRevokeResponse,
  UserExportRequest,
  UserExportResponse,
  CommunicationPreferencesRead,
  CommunicationPreferencesUpdate,
  MFASetupResponse,
  MFAVerifyRequest,
  MFAVerifyResponse,
  MFADisableRequest,
  MFADisableResponse,
  DeviceTokenRequest,
  DeviceTokenResponse,
  DeviceTokenDeleteRequest,
  OrganizationRead,
  OrganizationCreate,
  OrganizationUpdate,
  MemberRead,
  InvitationCreate,
  InvitationRead,
  token,
  TelemetryEvent,
  TelemetryResponse,
};

const endpoints = makeApi([
  {
    method: "post",
    path: "/api/v1/admin/impersonate/:patient_id",
    alias: "impersonate_patient_api_v1_admin_impersonate__patient_id__post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ reason: z.string() }).passthrough(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/consent",
    alias: "sign_consent_api_v1_consent_post",
    description: `Sign a specific consent document.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ document_id: z.string() }).passthrough(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/consent/required",
    alias: "get_required_consents_api_v1_consent_required_get",
    description: `List all active consents and status for the current user.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/v1/events",
    alias: "get_events_api_v1_events_get",
    description: `Server-Sent Events stream for real-time updates.

This endpoint establishes a long-lived HTTP connection for
server-to-client push notifications.

The client will receive events such as:
- notification.new: New notification created
- message.new: New message in subscribed thread
- appointment.reminder: Upcoming appointment reminder
- appointment.updated: Appointment rescheduled/cancelled
- document.processed: Document finished OCR/virus scan
- document.scan_complete: Virus scan completed
- consent.required: New consent document available
- call.incoming: Incoming call (Call Center)
- call.completed: Call ended
- heartbeat: Keep-alive (every 30 seconds)

Authentication can be provided via:
- Authorization header: Bearer {token}
- Query parameter: ?token&#x3D;{token}

Returns:
    StreamingResponse with text/event-stream content type`,
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Query",
        schema: token,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/events/organizations/:org_id",
    alias: "get_org_events_api_v1_events_organizations__org_id__get",
    description: `Organization-scoped SSE stream for admin views.

This endpoint provides organization-level events in addition
to standard user events. Requires ADMIN or SUPER_ADMIN role.

Additional event types:
- member.joined: New member accepted invitation
- member.removed: Member removed from organization
- subscription.updated: Subscription status changed
- license.expiring: Provider license expiring soon

Args:
    org_id: Organization ID

Returns:
    StreamingResponse with text/event-stream content type

Raises:
    HTTPException: If user is not admin of the organization`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "token",
        type: "Query",
        schema: token,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/invitations/:token",
    alias: "get_invitation_api_v1_invitations__token__get",
    description: `Get invitation details from token. Public endpoint.`,
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: InvitationRead,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/invitations/:token/accept",
    alias: "accept_invitation_api_v1_invitations__token__accept_post",
    description: `Accept an invitation. Requires user to be logged in.`,
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: InvitationRead,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/organizations",
    alias: "list_organizations_api_v1_organizations_get",
    description: `List all organizations the current user is a member of.`,
    requestFormat: "json",
    response: z.array(OrganizationRead),
  },
  {
    method: "post",
    path: "/api/v1/organizations",
    alias: "create_organization_api_v1_organizations_post",
    description: `Create a new organization and make the current user an ADMIN.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: OrganizationCreate,
      },
    ],
    response: OrganizationRead,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/organizations/:org_id",
    alias: "get_organization_api_v1_organizations__org_id__get",
    description: `Get organization details. Requires membership.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: OrganizationRead,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/v1/organizations/:org_id",
    alias: "update_organization_api_v1_organizations__org_id__patch",
    description: `Update organization. Requires ADMIN role.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: OrganizationUpdate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: OrganizationRead,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/organizations/:org_id/invitations",
    alias: "create_invitation_api_v1_organizations__org_id__invitations_post",
    description: `Invite a user to the organization. Requires ADMIN role.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: InvitationCreate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: InvitationRead,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/organizations/:org_id/invitations",
    alias: "list_invitations_api_v1_organizations__org_id__invitations_get",
    description: `List pending invitations. Requires ADMIN role.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.array(InvitationRead),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/organizations/:org_id/members",
    alias: "list_members_api_v1_organizations__org_id__members_get",
    description: `List members of an organization. Requires membership.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.array(MemberRead),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/telemetry",
    alias: "log_telemetry_event_api_v1_telemetry_post",
    description: `Log a behavioral analytics event.

This endpoint accepts telemetry events from the frontend and logs them
using structlog with &#x60;event_type&#x3D;&quot;analytics&quot;&#x60; for CloudWatch filtering.

**Use Cases:**
- Page views and navigation patterns
- Feature usage tracking
- Button clicks and user interactions
- Error events (client-side)
- Performance metrics

**Privacy:**
- Do not send PII/PHI in the properties
- User ID is automatically attached from context
- IP address is logged for basic analytics

Args:
    event: The telemetry event with name and properties

Returns:
    Confirmation that the event was logged`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TelemetryEvent,
      },
    ],
    response: TelemetryResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/telemetry/batch",
    alias: "log_telemetry_batch_api_v1_telemetry_batch_post",
    description: `Log multiple telemetry events in a batch.

This endpoint is optimized for sending multiple events at once,
reducing the number of HTTP requests from the frontend.

**Use Cases:**
- Offline event buffering
- Page unload event flushing
- Session aggregation

Args:
    events: List of telemetry events

Returns:
    Confirmation that all events were logged`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.array(TelemetryEvent),
      },
    ],
    response: TelemetryResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/users/device-token",
    alias: "register_device_token_api_v1_users_device_token_post",
    description: `Register an FCM token for push notifications.

If the token already exists for this user, updates the device info.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DeviceTokenRequest,
      },
    ],
    response: z
      .object({ success: z.boolean().default(true) })
      .partial()
      .passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/users/device-token",
    alias: "remove_device_token_api_v1_users_device_token_delete",
    description: `Remove an FCM token (logout cleanup).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ token: z.string().min(1).max(512) }).passthrough(),
      },
    ],
    response: z
      .object({ success: z.boolean().default(true) })
      .partial()
      .passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/users/me",
    alias: "read_users_me_api_v1_users_me_get",
    description: `Get current user profile.`,
    requestFormat: "json",
    response: UserRead,
  },
  {
    method: "delete",
    path: "/api/v1/users/me",
    alias: "delete_users_me_api_v1_users_me_delete",
    description: `Soft delete user account (HIPAA compliance - data retained).

This action cannot be undone. The account becomes inaccessible but
data is retained for legal compliance.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: UserDeleteRequest,
      },
    ],
    response: UserDeleteResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/v1/users/me",
    alias: "update_users_me_api_v1_users_me_patch",
    description: `Update current user&#x27;s profile.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: UserUpdate,
      },
    ],
    response: UserRead,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/users/me/communication-preferences",
    alias:
      "get_communication_preferences_api_v1_users_me_communication_preferences_get",
    description: `Get user&#x27;s communication opt-in status.`,
    requestFormat: "json",
    response: CommunicationPreferencesRead,
  },
  {
    method: "patch",
    path: "/api/v1/users/me/communication-preferences",
    alias:
      "update_communication_preferences_api_v1_users_me_communication_preferences_patch",
    description: `Update communication preferences.

Per TCPA compliance, transactional_consent must be True for appointment
reminders and billing alerts. marketing_consent controls promotional
communications.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CommunicationPreferencesUpdate,
      },
    ],
    response: CommunicationPreferencesRead,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/users/me/export",
    alias: "request_export_api_v1_users_me_export_post",
    description: `Request a HIPAA data export.

This initiates a background job. The user receives an email with a
secure download link when the export is ready (typically 24-48 hours).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: UserExportRequest,
      },
    ],
    response: UserExportResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/users/me/mfa/disable",
    alias: "mfa_disable_api_v1_users_me_mfa_disable_post",
    description: `Disable MFA for the account.

Requires password confirmation for security.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ password: z.string().min(1) }).passthrough(),
      },
    ],
    response: MFADisableResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/users/me/mfa/setup",
    alias: "mfa_setup_api_v1_users_me_mfa_setup_post",
    description: `Initialize MFA setup.

Returns a TOTP secret and provisioning URI for authenticator apps.
The secret is stored temporarily until verified.`,
    requestFormat: "json",
    response: MFASetupResponse,
  },
  {
    method: "post",
    path: "/api/v1/users/me/mfa/verify",
    alias: "mfa_verify_api_v1_users_me_mfa_verify_post",
    description: `Complete MFA setup by verifying a TOTP code.

Returns backup codes (shown only once - user must save them).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({
            code: z
              .string()
              .min(6)
              .max(6)
              .regex(/^[0-9]{6}$/),
          })
          .passthrough(),
      },
    ],
    response: MFAVerifyResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/users/me/sessions",
    alias: "list_sessions_api_v1_users_me_sessions_get",
    description: `List all active sessions for the current user.`,
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
      {
        name: "offset",
        type: "Query",
        schema: z.number().int().optional().default(0),
      },
    ],
    response: SessionListResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/v1/users/me/sessions/:session_id",
    alias: "revoke_session_api_v1_users_me_sessions__session_id__delete",
    description: `Terminate a specific session.

If session_id matches the current session, this is equivalent to logout.`,
    requestFormat: "json",
    parameters: [
      {
        name: "session_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: SessionRevokeResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/webhooks/stripe",
    alias: "handle_stripe_webhook_api_v1_webhooks_stripe_post",
    description: `Handle incoming Stripe webhook events.

This endpoint receives events from Stripe and processes them:
- Verifies the webhook signature for security
- Parses the event and dispatches to appropriate handlers
- Updates database records based on event type

**Security:**
- Signature verification using STRIPE_WEBHOOK_SECRET
- Raw body parsing to prevent tampering

**Handled Events:**
- checkout.session.completed: Subscription activated
- invoice.payment_succeeded: Payment confirmed
- invoice.payment_failed: Payment failed, status updated
- customer.subscription.updated: Subscription status changed
- customer.subscription.deleted: Subscription canceled

Returns:
    Success response for Stripe acknowledgment`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/health",
    alias: "health_check_health_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/health/deep",
    alias: "deep_health_check_health_deep_get",
    requestFormat: "json",
    response: z.unknown(),
  },
]);

export const api = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
