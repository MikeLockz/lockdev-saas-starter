import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

export const ImpersonationRequest = z
  .object({ reason: z.string() })
  .passthrough();
export const ValidationError = z
  .object({
    loc: z.array(z.union([z.string(), z.number()])),
    msg: z.string(),
    type: z.string(),
  })
  .passthrough();
export const HTTPValidationError = z
  .object({ detail: z.array(ValidationError) })
  .partial()
  .passthrough();
export const action_type = z.union([z.string(), z.null()]).optional();
export const AuditLogRead = z
  .object({
    action_type: z.string(),
    resource_type: z.string(),
    resource_id: z.string().uuid(),
    changes_json: z
      .union([z.object({}).partial().passthrough(), z.null()])
      .optional(),
    id: z.string().uuid(),
    actor_user_id: z.union([z.string(), z.null()]),
    organization_id: z.union([z.string(), z.null()]),
    ip_address: z.union([z.string(), z.string(), z.null()]),
    user_agent: z.union([z.string(), z.null()]),
    impersonator_id: z.union([z.string(), z.null()]),
    occurred_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const AuditLogListResponse = z
  .object({
    items: z.array(AuditLogRead),
    total: z.number().int(),
    page: z.number().int(),
    page_size: z.number().int(),
  })
  .passthrough();
export const OrganizationAdminRead = z
  .object({
    id: z.string().uuid(),
    name: z.string(),
    member_count: z.number().int(),
    patient_count: z.number().int(),
    subscription_status: z.string(),
    is_active: z.boolean(),
    created_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const OrganizationListResponse = z
  .object({
    items: z.array(OrganizationAdminRead),
    total: z.number().int(),
    page: z.number().int(),
    page_size: z.number().int(),
  })
  .passthrough();
export const OrganizationCreate = z
  .object({
    name: z.string(),
    subscription_status: z.string().optional().default("trial"),
  })
  .passthrough();
export const OrganizationUpdate = z
  .object({
    is_active: z.union([z.boolean(), z.null()]),
    subscription_status: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
export const is_locked = z.union([z.boolean(), z.null()]).optional();
export const UserAdminRead = z
  .object({
    id: z.string().uuid(),
    email: z.string(),
    display_name: z.union([z.string(), z.null()]),
    is_super_admin: z.boolean(),
    locked_until: z.union([z.string(), z.null()]),
    failed_login_attempts: z.number().int(),
    last_login_at: z.union([z.string(), z.null()]),
    created_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const UserListResponse = z
  .object({
    items: z.array(UserAdminRead),
    total: z.number().int(),
    page: z.number().int(),
    page_size: z.number().int(),
  })
  .passthrough();
export const UserAdminUpdate = z
  .object({ is_super_admin: z.union([z.boolean(), z.null()]) })
  .partial()
  .passthrough();
export const SystemHealth = z
  .object({
    db_status: z.string(),
    redis_status: z.string(),
    worker_status: z.string(),
    metrics: z.object({}).partial().passthrough(),
  })
  .passthrough();
export const ConsentSignRequest = z
  .object({ document_id: z.string() })
  .passthrough();
export const UserRead = z
  .object({
    id: z.string().uuid(),
    email: z.string().email(),
    display_name: z.union([z.string(), z.null()]).optional(),
    is_super_admin: z.boolean().optional().default(false),
    mfa_enabled: z.boolean().optional().default(false),
    requires_consent: z.boolean().optional().default(true),
    transactional_consent: z.boolean().optional().default(true),
    marketing_consent: z.boolean().optional().default(false),
    timezone: z.union([z.string(), z.null()]).optional(),
    effective_timezone: z.string().optional().default("America/New_York"),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const UserDeleteRequest = z
  .object({
    password: z.string().min(1),
    reason: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const UserDeleteResponse = z
  .object({
    success: z.boolean().optional().default(true),
    deleted_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const UserUpdate = z
  .object({
    display_name: z.union([z.string(), z.null()]),
    timezone: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
export const SessionRead = z
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
export const SessionListResponse = z
  .object({
    items: z.array(SessionRead),
    total: z.number().int(),
    limit: z.number().int().optional().default(50),
    offset: z.number().int().optional().default(0),
  })
  .passthrough();
export const SessionRevokeResponse = z
  .object({
    success: z.boolean().optional().default(true),
    terminated_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const UserExportRequest = z
  .object({
    format: z
      .string()
      .regex(/^(json|pdf)$/)
      .default("json"),
    include_documents: z.boolean().default(false),
  })
  .partial()
  .passthrough();
export const UserExportResponse = z
  .object({
    export_id: z.string().uuid(),
    status: z.string().optional().default("PENDING"),
    estimated_completion: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const CommunicationPreferencesRead = z
  .object({
    transactional_consent: z.boolean(),
    marketing_consent: z.boolean(),
    updated_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const CommunicationPreferencesUpdate = z
  .object({
    transactional_consent: z.union([z.boolean(), z.null()]),
    marketing_consent: z.union([z.boolean(), z.null()]),
  })
  .partial()
  .passthrough();
export const TimezoneResponse = z
  .object({ timezone: z.string(), source: z.string() })
  .passthrough();
export const TimezoneUpdateRequest = z
  .object({ timezone: z.string() })
  .passthrough();
export const MFASetupResponse = z
  .object({
    secret: z.string(),
    provisioning_uri: z.string(),
    qr_code_data_url: z.union([z.string(), z.null()]).optional(),
    expires_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const MFAVerifyRequest = z
  .object({
    code: z
      .string()
      .min(6)
      .max(6)
      .regex(/^[0-9]{6}$/),
  })
  .passthrough();
export const MFAVerifyResponse = z
  .object({
    success: z.boolean().optional().default(true),
    mfa_enabled: z.boolean().optional().default(true),
    backup_codes: z.array(z.string()),
    enabled_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const MFADisableRequest = z
  .object({ password: z.string().min(1) })
  .passthrough();
export const MFADisableResponse = z
  .object({
    success: z.boolean().optional().default(true),
    mfa_enabled: z.boolean().optional().default(false),
    disabled_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const DeviceTokenRequest = z
  .object({
    token: z.string().min(1).max(512),
    platform: z.string().regex(/^(ios|android|web)$/),
    device_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const DeviceTokenResponse = z
  .object({ success: z.boolean().default(true) })
  .partial()
  .passthrough();
export const DeviceTokenDeleteRequest = z
  .object({ token: z.string().min(1).max(512) })
  .passthrough();
export const ProxyPatientInfo = z
  .object({
    id: z.string().uuid(),
    first_name: z.string(),
    last_name: z.string(),
    dob: z.string(),
    medical_record_number: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const ProxyPermissions = z
  .object({
    can_view_profile: z.boolean().default(true),
    can_view_appointments: z.boolean().default(true),
    can_schedule_appointments: z.boolean().default(false),
    can_view_clinical_notes: z.boolean().default(false),
    can_view_billing: z.boolean().default(false),
    can_message_providers: z.boolean().default(false),
  })
  .partial()
  .passthrough();
export const ProxyPatientRead = z
  .object({
    patient: ProxyPatientInfo,
    relationship_type: z.string(),
    permissions: ProxyPermissions,
    granted_at: z.string().datetime({ offset: true }),
    expires_at: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const ProxyProfileRead = z
  .object({
    id: z.string().uuid(),
    user_id: z.string().uuid(),
    relationship_to_patient: z.union([z.string(), z.null()]).optional(),
    created_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const OrganizationRead = z
  .object({
    name: z.string().max(255),
    tax_id: z.union([z.string(), z.null()]).optional(),
    settings_json: z.object({}).partial().passthrough().optional(),
    timezone: z.string().max(50).optional().default("America/New_York"),
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
export const src__schemas__organizations__OrganizationCreate = z
  .object({
    name: z.string().max(255),
    tax_id: z.union([z.string(), z.null()]).optional(),
    settings_json: z.object({}).partial().passthrough().optional(),
    timezone: z.string().max(50).optional().default("America/New_York"),
  })
  .passthrough();
export const src__schemas__organizations__OrganizationUpdate = z
  .object({
    name: z.union([z.string(), z.null()]),
    tax_id: z.union([z.string(), z.null()]),
    settings_json: z.union([z.object({}).partial().passthrough(), z.null()]),
    timezone: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
export const MemberRead = z
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
export const InvitationCreate = z
  .object({ email: z.string().email(), role: z.string() })
  .passthrough();
export const InvitationRead = z
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
export const ContactMethodCreate = z
  .object({
    type: z.string(),
    value: z.string(),
    is_primary: z.boolean().optional().default(false),
    is_safe_for_voicemail: z.boolean().optional().default(false),
    label: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const PatientCreate = z
  .object({
    first_name: z.string().max(100),
    last_name: z.string().max(100),
    dob: z.string(),
    legal_sex: z.union([z.string(), z.null()]).optional(),
    medical_record_number: z.union([z.string(), z.null()]).optional(),
    contact_methods: z
      .union([z.array(ContactMethodCreate), z.null()])
      .optional(),
  })
  .passthrough();
export const ContactMethodRead = z
  .object({
    id: z.string().uuid(),
    type: z.string(),
    value: z.string(),
    is_primary: z.boolean(),
    is_safe_for_voicemail: z.boolean(),
    label: z.union([z.string(), z.null()]),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const PatientRead = z
  .object({
    id: z.string().uuid(),
    user_id: z.union([z.string(), z.null()]),
    first_name: z.string(),
    last_name: z.string(),
    dob: z.string(),
    legal_sex: z.union([z.string(), z.null()]),
    medical_record_number: z.union([z.string(), z.null()]),
    stripe_customer_id: z.union([z.string(), z.null()]),
    subscription_status: z.string(),
    contact_methods: z.array(ContactMethodRead).optional().default([]),
    enrolled_at: z.union([z.string(), z.null()]).optional(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const PatientListItem = z
  .object({
    id: z.string().uuid(),
    first_name: z.string(),
    last_name: z.string(),
    dob: z.string(),
    medical_record_number: z.union([z.string(), z.null()]),
    enrolled_at: z.union([z.string(), z.null()]).optional(),
    status: z.string().optional().default("ACTIVE"),
  })
  .passthrough();
export const PaginatedPatients = z
  .object({
    items: z.array(PatientListItem),
    total: z.number().int(),
    limit: z.number().int(),
    offset: z.number().int(),
  })
  .passthrough();
export const PatientUpdate = z
  .object({
    first_name: z.union([z.string(), z.null()]),
    last_name: z.union([z.string(), z.null()]),
    dob: z.union([z.string(), z.null()]),
    legal_sex: z.union([z.string(), z.null()]),
    medical_record_number: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
export const ContactMethodUpdate = z
  .object({
    type: z.union([z.string(), z.null()]),
    value: z.union([z.string(), z.null()]),
    is_primary: z.union([z.boolean(), z.null()]),
    is_safe_for_voicemail: z.union([z.boolean(), z.null()]),
    label: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
export const CareTeamMember = z
  .object({
    assignment_id: z.string().uuid(),
    provider_id: z.string().uuid(),
    role: z.string(),
    assigned_at: z.string().datetime({ offset: true }),
    provider_name: z.union([z.string(), z.null()]).optional(),
    provider_specialty: z.union([z.string(), z.null()]).optional(),
    provider_npi: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const CareTeamList = z
  .object({
    patient_id: z.string().uuid(),
    members: z.array(CareTeamMember),
    primary_provider: z.union([CareTeamMember, z.null()]).optional(),
  })
  .passthrough();
export const CareTeamAssignmentCreate = z
  .object({
    provider_id: z.string().uuid(),
    role: z.string().optional().default("SPECIALIST"),
  })
  .passthrough();
export const CareTeamProviderInfo = z
  .object({
    id: z.string().uuid(),
    user_id: z.string().uuid(),
    npi_number: z.union([z.string(), z.null()]).optional(),
    specialty: z.union([z.string(), z.null()]).optional(),
    user_display_name: z.union([z.string(), z.null()]).optional(),
    user_email: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const CareTeamAssignmentRead = z
  .object({
    id: z.string().uuid(),
    patient_id: z.string().uuid(),
    provider_id: z.string().uuid(),
    role: z.string(),
    assigned_at: z.string().datetime({ offset: true }),
    removed_at: z.union([z.string(), z.null()]).optional(),
    provider: CareTeamProviderInfo,
  })
  .passthrough();
export const ProviderCreate = z
  .object({
    user_id: z.string().uuid(),
    npi_number: z.union([z.string(), z.null()]).optional(),
    specialty: z.union([z.string(), z.null()]).optional(),
    license_number: z.union([z.string(), z.null()]).optional(),
    license_state: z.union([z.string(), z.null()]).optional(),
    dea_number: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const ProviderRead = z
  .object({
    id: z.string().uuid(),
    user_id: z.string().uuid(),
    organization_id: z.string().uuid(),
    npi_number: z.union([z.string(), z.null()]),
    specialty: z.union([z.string(), z.null()]),
    license_number: z.union([z.string(), z.null()]),
    license_state: z.union([z.string(), z.null()]),
    dea_number: z.union([z.string(), z.null()]),
    state_licenses: z.array(z.unknown()),
    is_active: z.boolean(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    user_email: z.union([z.string(), z.null()]).optional(),
    user_display_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const ProviderListItem = z
  .object({
    id: z.string().uuid(),
    user_id: z.string().uuid(),
    npi_number: z.union([z.string(), z.null()]),
    specialty: z.union([z.string(), z.null()]),
    is_active: z.boolean(),
    user_email: z.union([z.string(), z.null()]).optional(),
    user_display_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const PaginatedProviders = z
  .object({
    items: z.array(ProviderListItem),
    total: z.number().int(),
    limit: z.number().int(),
    offset: z.number().int(),
  })
  .passthrough();
export const ProviderUpdate = z
  .object({
    npi_number: z.union([z.string(), z.null()]),
    specialty: z.union([z.string(), z.null()]),
    license_number: z.union([z.string(), z.null()]),
    license_state: z.union([z.string(), z.null()]),
    dea_number: z.union([z.string(), z.null()]),
    is_active: z.union([z.boolean(), z.null()]),
  })
  .partial()
  .passthrough();
export const StaffCreate = z
  .object({
    user_id: z.string().uuid(),
    job_title: z.union([z.string(), z.null()]).optional(),
    department: z.union([z.string(), z.null()]).optional(),
    employee_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const StaffRead = z
  .object({
    id: z.string().uuid(),
    user_id: z.string().uuid(),
    organization_id: z.string().uuid(),
    job_title: z.union([z.string(), z.null()]),
    department: z.union([z.string(), z.null()]),
    employee_id: z.union([z.string(), z.null()]),
    is_active: z.boolean(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    user_email: z.union([z.string(), z.null()]).optional(),
    user_display_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const StaffListItem = z
  .object({
    id: z.string().uuid(),
    user_id: z.string().uuid(),
    job_title: z.union([z.string(), z.null()]),
    department: z.union([z.string(), z.null()]),
    is_active: z.boolean(),
    user_email: z.union([z.string(), z.null()]).optional(),
    user_display_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const PaginatedStaff = z
  .object({
    items: z.array(StaffListItem),
    total: z.number().int(),
    limit: z.number().int(),
    offset: z.number().int(),
  })
  .passthrough();
export const StaffUpdate = z
  .object({
    job_title: z.union([z.string(), z.null()]),
    department: z.union([z.string(), z.null()]),
    employee_id: z.union([z.string(), z.null()]),
    is_active: z.union([z.boolean(), z.null()]),
  })
  .partial()
  .passthrough();
export const AppointmentCreate = z
  .object({
    scheduled_at: z.string().datetime({ offset: true }),
    duration_minutes: z.number().int().gte(5).lte(480).optional().default(30),
    appointment_type: z.string().optional().default("FOLLOW_UP"),
    reason: z.union([z.string(), z.null()]).optional(),
    notes: z.union([z.string(), z.null()]).optional(),
    patient_id: z.string().uuid(),
    provider_id: z.string().uuid(),
  })
  .passthrough();
export const AppointmentRead = z
  .object({
    scheduled_at: z.string().datetime({ offset: true }),
    duration_minutes: z.number().int().gte(5).lte(480).optional().default(30),
    appointment_type: z.string().optional().default("FOLLOW_UP"),
    reason: z.union([z.string(), z.null()]).optional(),
    notes: z.union([z.string(), z.null()]).optional(),
    id: z.string().uuid(),
    organization_id: z.string().uuid(),
    patient_id: z.string().uuid(),
    provider_id: z.string().uuid(),
    status: z.string(),
    cancelled_at: z.union([z.string(), z.null()]).optional(),
    cancelled_by: z.union([z.string(), z.null()]).optional(),
    cancellation_reason: z.union([z.string(), z.null()]).optional(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    patient_name: z.union([z.string(), z.null()]).optional(),
    provider_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const AppointmentUpdate = z
  .object({
    scheduled_at: z.union([z.string(), z.null()]),
    duration_minutes: z.union([z.number(), z.null()]),
    appointment_type: z.union([z.string(), z.null()]),
    reason: z.union([z.string(), z.null()]),
    notes: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
export const AppointmentStatusUpdate = z
  .object({
    status: z.string(),
    cancellation_reason: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const DocumentUploadRequest = z
  .object({
    file_name: z.string().min(1).max(255),
    file_type: z.string().max(100).optional().default("application/pdf"),
    file_size: z.number().int().gt(0).lte(10485760),
    document_type: z.string().optional().default("OTHER"),
    description: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const DocumentUploadResponse = z
  .object({
    document_id: z.string().uuid(),
    upload_url: z.string(),
    upload_fields: z.object({}).partial().passthrough(),
    s3_key: z.string(),
  })
  .passthrough();
export const DocumentRead = z
  .object({
    id: z.string().uuid(),
    organization_id: z.string().uuid(),
    patient_id: z.string().uuid(),
    uploaded_by_user_id: z.string().uuid(),
    file_name: z.string(),
    file_type: z.string(),
    file_size: z.number().int(),
    s3_key: z.string(),
    document_type: z.string(),
    description: z.union([z.string(), z.null()]),
    status: z.string(),
    uploaded_at: z.union([z.string(), z.null()]),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    uploaded_by_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const DocumentListItem = z
  .object({
    id: z.string().uuid(),
    file_name: z.string(),
    file_type: z.string(),
    file_size: z.number().int(),
    document_type: z.string(),
    status: z.string(),
    uploaded_at: z.union([z.string(), z.null()]),
    uploaded_by_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const PaginatedDocuments = z
  .object({
    items: z.array(DocumentListItem),
    total: z.number().int(),
    limit: z.number().int(),
    offset: z.number().int(),
  })
  .passthrough();
export const DocumentDownloadResponse = z
  .object({
    document_id: z.string().uuid(),
    download_url: z.string(),
    expires_in: z.number().int().optional().default(3600),
  })
  .passthrough();
export const ProxyUserInfo = z
  .object({
    id: z.string().uuid(),
    email: z.string(),
    display_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const ProxyAssignmentRead = z
  .object({
    id: z.string().uuid(),
    proxy_id: z.string().uuid(),
    patient_id: z.string().uuid(),
    relationship_type: z.string(),
    can_view_profile: z.boolean(),
    can_view_appointments: z.boolean(),
    can_schedule_appointments: z.boolean(),
    can_view_clinical_notes: z.boolean(),
    can_view_billing: z.boolean(),
    can_message_providers: z.boolean(),
    granted_at: z.string().datetime({ offset: true }),
    expires_at: z.union([z.string(), z.null()]).optional(),
    revoked_at: z.union([z.string(), z.null()]).optional(),
    user: ProxyUserInfo,
  })
  .passthrough();
export const ProxyListResponse = z
  .object({
    patient_id: z.string().uuid(),
    proxies: z.array(ProxyAssignmentRead),
  })
  .passthrough();
export const ProxyAssignmentCreate = z
  .object({
    email: z.string().email(),
    relationship_type: z.string(),
    permissions: ProxyPermissions.optional(),
    expires_at: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const ProxyAssignmentUpdate = z
  .object({
    permissions: z.union([ProxyPermissions, z.null()]),
    expires_at: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
export const TelemetryEvent = z
  .object({
    event_name: z.string().min(1).max(100),
    properties: z.object({}).partial().passthrough().optional(),
  })
  .passthrough();
export const TelemetryResponse = z
  .object({
    success: z.boolean().default(true),
    event_id: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
export const CheckoutSessionRequest = z
  .object({ price_id: z.string() })
  .passthrough();
export const CheckoutSessionResponse = z
  .object({ session_id: z.string(), checkout_url: z.string() })
  .passthrough();
export const SubscriptionStatusResponse = z
  .object({
    status: z.string(),
    plan_id: z.union([z.string(), z.null()]).optional(),
    current_period_end: z.union([z.number(), z.null()]).optional(),
    cancel_at_period_end: z.boolean().optional().default(false),
  })
  .passthrough();
export const PortalSessionResponse = z
  .object({ portal_url: z.string() })
  .passthrough();
export const NotificationRead = z
  .object({
    id: z.string().uuid(),
    type: z.string(),
    title: z.string(),
    body: z.union([z.string(), z.null()]).optional(),
    data_json: z
      .union([z.object({}).partial().passthrough(), z.null()])
      .optional(),
    is_read: z.boolean(),
    read_at: z.union([z.string(), z.null()]).optional(),
    created_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const NotificationListResponse = z
  .object({
    items: z.array(NotificationRead),
    total: z.number().int(),
    unread_count: z.number().int(),
    page: z.number().int(),
    size: z.number().int(),
  })
  .passthrough();
export const UnreadCountResponse = z
  .object({ count: z.number().int() })
  .passthrough();
export const MessageRead = z
  .object({
    body: z.string(),
    id: z.string().uuid(),
    thread_id: z.string().uuid(),
    sender_id: z.union([z.string(), z.null()]),
    created_at: z.string().datetime({ offset: true }),
    sender_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const ParticipantRead = z
  .object({
    user_id: z.string().uuid(),
    joined_at: z.string().datetime({ offset: true }),
    last_read_at: z.union([z.string(), z.null()]),
    user_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const ThreadRead = z
  .object({
    subject: z.string(),
    id: z.string().uuid(),
    organization_id: z.string().uuid(),
    patient_id: z.union([z.string(), z.null()]),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    last_message: z.union([MessageRead, z.null()]).optional(),
    unread_count: z.number().int().optional().default(0),
    participants: z.array(ParticipantRead).optional().default([]),
  })
  .passthrough();
export const ThreadListResponse = z
  .object({
    items: z.array(ThreadRead),
    total: z.number().int(),
    page: z.number().int(),
    size: z.number().int(),
  })
  .passthrough();
export const ThreadCreate = z
  .object({
    subject: z.string(),
    organization_id: z.string().uuid(),
    patient_id: z.union([z.string(), z.null()]).optional(),
    initial_message: z.string(),
    participant_ids: z.array(z.string().uuid()),
  })
  .passthrough();
export const ThreadDetail = z
  .object({
    subject: z.string(),
    id: z.string().uuid(),
    organization_id: z.string().uuid(),
    patient_id: z.union([z.string(), z.null()]),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    last_message: z.union([MessageRead, z.null()]).optional(),
    unread_count: z.number().int().optional().default(0),
    participants: z.array(ParticipantRead).optional().default([]),
    messages: z.array(MessageRead).optional().default([]),
  })
  .passthrough();
export const MessageCreate = z.object({ body: z.string() }).passthrough();
export const CallRead = z
  .object({
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.union([z.string(), z.null()]).optional(),
    id: z.string().uuid(),
    direction: z.string(),
    phone_number: z.string(),
    notes: z.union([z.string(), z.null()]).optional(),
    outcome: z.union([z.string(), z.null()]).optional(),
    patient_id: z.union([z.string(), z.null()]).optional(),
    organization_id: z.string().uuid(),
    agent_id: z.string().uuid(),
    status: z.string(),
    started_at: z.union([z.string(), z.null()]),
    ended_at: z.union([z.string(), z.null()]),
    duration_seconds: z.union([z.number(), z.null()]),
    agent_name: z.union([z.string(), z.null()]).optional(),
    patient_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const CallCreate = z
  .object({
    direction: z.string(),
    phone_number: z.string(),
    notes: z.union([z.string(), z.null()]).optional(),
    outcome: z.union([z.string(), z.null()]).optional(),
    patient_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const CallUpdate = z
  .object({
    status: z.union([z.string(), z.null()]),
    notes: z.union([z.string(), z.null()]),
    outcome: z.union([z.string(), z.null()]),
    ended_at: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
export const TaskRead = z
  .object({
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.union([z.string(), z.null()]).optional(),
    id: z.string().uuid(),
    title: z.string(),
    description: z.union([z.string(), z.null()]).optional(),
    priority: z.string(),
    due_date: z.union([z.string(), z.null()]).optional(),
    patient_id: z.union([z.string(), z.null()]).optional(),
    assignee_id: z.string().uuid(),
    organization_id: z.string().uuid(),
    created_by_id: z.string().uuid(),
    status: z.string(),
    completed_at: z.union([z.string(), z.null()]),
    assignee_name: z.union([z.string(), z.null()]).optional(),
    patient_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
export const TaskCreate = z
  .object({
    title: z.string(),
    description: z.union([z.string(), z.null()]).optional(),
    priority: z.string(),
    due_date: z.union([z.string(), z.null()]).optional(),
    patient_id: z.union([z.string(), z.null()]).optional(),
    assignee_id: z.string().uuid(),
  })
  .passthrough();
export const TaskUpdate = z
  .object({
    title: z.union([z.string(), z.null()]),
    description: z.union([z.string(), z.null()]),
    priority: z.union([z.string(), z.null()]),
    status: z.union([z.string(), z.null()]),
    due_date: z.union([z.string(), z.null()]),
    assignee_id: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
export const SupportMessageRead = z
  .object({
    body: z.string(),
    id: z.string().uuid(),
    ticket_id: z.string().uuid(),
    sender_id: z.string().uuid(),
    is_internal: z.boolean(),
    created_at: z.string().datetime({ offset: true }),
  })
  .passthrough();
export const TicketRead = z
  .object({
    subject: z.string(),
    category: z.string(),
    priority: z.string(),
    id: z.string().uuid(),
    user_id: z.string().uuid(),
    organization_id: z.union([z.string(), z.null()]),
    status: z.string(),
    assigned_to_id: z.union([z.string(), z.null()]),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
    resolved_at: z.union([z.string(), z.null()]),
    message_count: z.number().int().optional().default(0),
    messages: z.array(SupportMessageRead).optional().default([]),
  })
  .passthrough();
export const TicketCreate = z
  .object({
    subject: z.string(),
    category: z.string(),
    priority: z.string(),
    initial_message: z.string(),
  })
  .passthrough();
export const SupportMessageCreate = z
  .object({
    body: z.string(),
    is_internal: z.boolean().optional().default(false),
  })
  .passthrough();
export const TicketUpdate = z
  .object({
    status: z.union([z.string(), z.null()]),
    priority: z.union([z.string(), z.null()]),
    assigned_to_id: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();

export const schemas = {
  ImpersonationRequest,
  ValidationError,
  HTTPValidationError,
  action_type,
  AuditLogRead,
  AuditLogListResponse,
  OrganizationAdminRead,
  OrganizationListResponse,
  OrganizationCreate,
  OrganizationUpdate,
  is_locked,
  UserAdminRead,
  UserListResponse,
  UserAdminUpdate,
  SystemHealth,
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
  TimezoneResponse,
  TimezoneUpdateRequest,
  MFASetupResponse,
  MFAVerifyRequest,
  MFAVerifyResponse,
  MFADisableRequest,
  MFADisableResponse,
  DeviceTokenRequest,
  DeviceTokenResponse,
  DeviceTokenDeleteRequest,
  ProxyPatientInfo,
  ProxyPermissions,
  ProxyPatientRead,
  ProxyProfileRead,
  OrganizationRead,
  src__schemas__organizations__OrganizationCreate,
  src__schemas__organizations__OrganizationUpdate,
  MemberRead,
  InvitationCreate,
  InvitationRead,
  ContactMethodCreate,
  PatientCreate,
  ContactMethodRead,
  PatientRead,
  PatientListItem,
  PaginatedPatients,
  PatientUpdate,
  ContactMethodUpdate,
  CareTeamMember,
  CareTeamList,
  CareTeamAssignmentCreate,
  CareTeamProviderInfo,
  CareTeamAssignmentRead,
  ProviderCreate,
  ProviderRead,
  ProviderListItem,
  PaginatedProviders,
  ProviderUpdate,
  StaffCreate,
  StaffRead,
  StaffListItem,
  PaginatedStaff,
  StaffUpdate,
  AppointmentCreate,
  AppointmentRead,
  AppointmentUpdate,
  AppointmentStatusUpdate,
  DocumentUploadRequest,
  DocumentUploadResponse,
  DocumentRead,
  DocumentListItem,
  PaginatedDocuments,
  DocumentDownloadResponse,
  ProxyUserInfo,
  ProxyAssignmentRead,
  ProxyListResponse,
  ProxyAssignmentCreate,
  ProxyAssignmentUpdate,
  TelemetryEvent,
  TelemetryResponse,
  CheckoutSessionRequest,
  CheckoutSessionResponse,
  SubscriptionStatusResponse,
  PortalSessionResponse,
  NotificationRead,
  NotificationListResponse,
  UnreadCountResponse,
  MessageRead,
  ParticipantRead,
  ThreadRead,
  ThreadListResponse,
  ThreadCreate,
  ThreadDetail,
  MessageCreate,
  CallRead,
  CallCreate,
  CallUpdate,
  TaskRead,
  TaskCreate,
  TaskUpdate,
  SupportMessageRead,
  TicketRead,
  TicketCreate,
  SupportMessageCreate,
  TicketUpdate,
};

export const endpoints = makeApi([
  {
    method: "get",
    path: "/api/v1/admin/audit-logs",
    alias: "list_audit_logs_api_v1_admin_audit_logs_get",
    description: `List audit logs with optional filtering.
Requires admin privileges.`,
    requestFormat: "json",
    parameters: [
      {
        name: "action_type",
        type: "Query",
        schema: action_type,
      },
      {
        name: "resource_type",
        type: "Query",
        schema: action_type,
      },
      {
        name: "resource_id",
        type: "Query",
        schema: action_type,
      },
      {
        name: "actor_user_id",
        type: "Query",
        schema: action_type,
      },
      {
        name: "date_from",
        type: "Query",
        schema: action_type,
      },
      {
        name: "date_to",
        type: "Query",
        schema: action_type,
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().gte(1).optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(50),
      },
    ],
    response: AuditLogListResponse,
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
    path: "/api/v1/admin/audit-logs/:log_id",
    alias: "get_audit_log_api_v1_admin_audit_logs__log_id__get",
    description: `Get a specific audit log entry.`,
    requestFormat: "json",
    parameters: [
      {
        name: "log_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: AuditLogRead,
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
    path: "/api/v1/admin/audit-logs/export",
    alias: "export_audit_logs_api_v1_admin_audit_logs_export_get",
    description: `Export audit logs as CSV.`,
    requestFormat: "json",
    parameters: [
      {
        name: "action_type",
        type: "Query",
        schema: action_type,
      },
      {
        name: "resource_type",
        type: "Query",
        schema: action_type,
      },
      {
        name: "resource_id",
        type: "Query",
        schema: action_type,
      },
      {
        name: "actor_user_id",
        type: "Query",
        schema: action_type,
      },
      {
        name: "date_from",
        type: "Query",
        schema: action_type,
      },
      {
        name: "date_to",
        type: "Query",
        schema: action_type,
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
    method: "get",
    path: "/api/v1/admin/super-admin/organizations",
    alias: "list_all_organizations_api_v1_admin_super_admin_organizations_get",
    description: `List all organizations across the platform.`,
    requestFormat: "json",
    parameters: [
      {
        name: "search",
        type: "Query",
        schema: action_type,
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().gte(1).optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(50),
      },
    ],
    response: OrganizationListResponse,
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
    path: "/api/v1/admin/super-admin/organizations",
    alias: "create_organization_api_v1_admin_super_admin_organizations_post",
    description: `Create a new organization (super admin only).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: OrganizationCreate,
      },
    ],
    response: OrganizationAdminRead,
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
    path: "/api/v1/admin/super-admin/organizations/:org_id",
    alias:
      "get_organization_detail_api_v1_admin_super_admin_organizations__org_id__get",
    description: `Get detailed organization info.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: OrganizationAdminRead,
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
    path: "/api/v1/admin/super-admin/organizations/:org_id",
    alias:
      "update_organization_api_v1_admin_super_admin_organizations__org_id__patch",
    description: `Update organization (suspend, activate, etc.).`,
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
    response: OrganizationAdminRead,
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
    path: "/api/v1/admin/super-admin/system",
    alias: "get_system_health_api_v1_admin_super_admin_system_get",
    description: `Get system health status.`,
    requestFormat: "json",
    response: SystemHealth,
  },
  {
    method: "get",
    path: "/api/v1/admin/super-admin/users",
    alias: "list_all_users_api_v1_admin_super_admin_users_get",
    description: `List all users across the platform.`,
    requestFormat: "json",
    parameters: [
      {
        name: "search",
        type: "Query",
        schema: action_type,
      },
      {
        name: "is_locked",
        type: "Query",
        schema: is_locked,
      },
      {
        name: "is_super_admin",
        type: "Query",
        schema: is_locked,
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().gte(1).optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(50),
      },
    ],
    response: UserListResponse,
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
    path: "/api/v1/admin/super-admin/users/:user_id",
    alias: "update_user_admin_api_v1_admin_super_admin_users__user_id__patch",
    description: `Update user (toggle super admin, etc.).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: UserAdminUpdate,
      },
      {
        name: "user_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: UserAdminRead,
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
    path: "/api/v1/admin/super-admin/users/:user_id/unlock",
    alias: "unlock_user_api_v1_admin_super_admin_users__user_id__unlock_patch",
    description: `Unlock a locked user account.`,
    requestFormat: "json",
    parameters: [
      {
        name: "user_id",
        type: "Path",
        schema: z.string().uuid(),
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
        schema: action_type,
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
        schema: action_type,
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
        schema: src__schemas__organizations__OrganizationCreate,
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
        schema: src__schemas__organizations__OrganizationUpdate,
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
    path: "/api/v1/organizations/:org_id/appointments",
    alias: "create_appointment_api_v1_organizations__org_id__appointments_post",
    description: `Create a new appointment.
Validates that the provider is not double-booked.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AppointmentCreate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: AppointmentRead,
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
    path: "/api/v1/organizations/:org_id/appointments",
    alias: "list_appointments_api_v1_organizations__org_id__appointments_get",
    description: `List appointments with filters.
Defaults to today&#x27;s appointments if no date filter is provided?
(Spec says &quot;Default: today&#x27;s appointments&quot; but let&#x27;s implement flexible filters first)`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "provider_id",
        type: "Query",
        schema: action_type,
      },
      {
        name: "patient_id",
        type: "Query",
        schema: action_type,
      },
      {
        name: "status",
        type: "Query",
        schema: action_type,
      },
      {
        name: "date_from",
        type: "Query",
        schema: action_type,
      },
      {
        name: "date_to",
        type: "Query",
        schema: action_type,
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(50),
      },
      {
        name: "offset",
        type: "Query",
        schema: z.number().int().gte(0).optional().default(0),
      },
    ],
    response: z.array(AppointmentRead),
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
    path: "/api/v1/organizations/:org_id/appointments/:appointment_id",
    alias:
      "get_appointment_api_v1_organizations__org_id__appointments__appointment_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "appointment_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: AppointmentRead,
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
    path: "/api/v1/organizations/:org_id/appointments/:appointment_id",
    alias:
      "update_appointment_api_v1_organizations__org_id__appointments__appointment_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AppointmentUpdate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "appointment_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: AppointmentRead,
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
    path: "/api/v1/organizations/:org_id/appointments/:appointment_id/status",
    alias:
      "update_appointment_status_api_v1_organizations__org_id__appointments__appointment_id__status_patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AppointmentStatusUpdate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "appointment_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: AppointmentRead,
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
    path: "/api/v1/organizations/:org_id/billing/checkout",
    alias:
      "create_checkout_api_v1_organizations__org_id__billing_checkout_post",
    description: `Create a Stripe Checkout Session for subscription.

Creates a Stripe customer for the organization if one doesn&#x27;t exist,
then creates a checkout session for the specified price.

**Requires**: Organization ADMIN role.

Returns:
    Checkout session with redirect URL for Stripe payment page.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ price_id: z.string() }).passthrough(),
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: CheckoutSessionResponse,
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
    path: "/api/v1/organizations/:org_id/billing/portal",
    alias:
      "create_billing_portal_api_v1_organizations__org_id__billing_portal_post",
    description: `Create a Stripe Customer Portal session.

The portal allows customers to manage their subscription,
update payment methods, and view invoices.

**Requires**: Organization ADMIN role.

Returns:
    Portal session with redirect URL.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.object({ portal_url: z.string() }).passthrough(),
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
    path: "/api/v1/organizations/:org_id/billing/subscription",
    alias:
      "get_subscription_status_api_v1_organizations__org_id__billing_subscription_get",
    description: `Get current subscription status for the organization.

**Requires**: Organization ADMIN role.

Returns:
    Current subscription status including plan and billing period.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: SubscriptionStatusResponse,
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
    path: "/api/v1/organizations/:org_id/calls/",
    alias: "list_calls_api_v1_organizations__org_id__calls__get",
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "status",
        type: "Query",
        schema: action_type,
      },
      {
        name: "agent_id",
        type: "Query",
        schema: action_type,
      },
      {
        name: "date_from",
        type: "Query",
        schema: action_type,
      },
      {
        name: "date_to",
        type: "Query",
        schema: action_type,
      },
      {
        name: "skip",
        type: "Query",
        schema: z.number().int().optional().default(0),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
    ],
    response: z.array(CallRead),
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
    path: "/api/v1/organizations/:org_id/calls/",
    alias: "create_call_api_v1_organizations__org_id__calls__post",
    description: `Log a new call. Automatically sets status to IN_PROGRESS and started_at to now.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CallCreate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: CallRead,
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
    path: "/api/v1/organizations/:org_id/calls/:call_id",
    alias: "update_call_api_v1_organizations__org_id__calls__call_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CallUpdate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "call_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: CallRead,
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
    path: "/api/v1/organizations/:org_id/patients",
    alias: "create_patient_api_v1_organizations__org_id__patients_post",
    description: `Create a new patient and enroll in the organization.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PatientCreate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: PatientRead,
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
    path: "/api/v1/organizations/:org_id/patients",
    alias: "list_patients_api_v1_organizations__org_id__patients_get",
    description: `List patients enrolled in the organization with optional filters.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "name",
        type: "Query",
        schema: action_type,
      },
      {
        name: "mrn",
        type: "Query",
        schema: action_type,
      },
      {
        name: "status",
        type: "Query",
        schema: action_type,
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(50),
      },
      {
        name: "offset",
        type: "Query",
        schema: z.number().int().gte(0).optional().default(0),
      },
    ],
    response: PaginatedPatients,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id",
    alias:
      "get_patient_api_v1_organizations__org_id__patients__patient_id__get",
    description: `Get full patient details with contact methods.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: PatientRead,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id",
    alias:
      "update_patient_api_v1_organizations__org_id__patients__patient_id__patch",
    description: `Update patient fields. Requires org membership.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PatientUpdate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: PatientRead,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id",
    alias:
      "discharge_patient_api_v1_organizations__org_id__patients__patient_id__delete",
    description: `Discharge a patient from the organization (soft delete via status change).`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.void(),
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/care-team",
    alias:
      "get_care_team_api_v1_organizations__org_id__patients__patient_id__care_team_get",
    description: `Get all providers assigned to a patient&#x27;s care team.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: CareTeamList,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/care-team",
    alias:
      "assign_to_care_team_api_v1_organizations__org_id__patients__patient_id__care_team_post",
    description: `Assign a provider to a patient&#x27;s care team.
Only one PRIMARY provider allowed per patient.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CareTeamAssignmentCreate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: CareTeamAssignmentRead,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/care-team/:assignment_id",
    alias:
      "remove_from_care_team_api_v1_organizations__org_id__patients__patient_id__care_team__assignment_id__delete",
    description: `Remove a provider from a patient&#x27;s care team (soft delete).`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "assignment_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.void(),
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/contact-methods",
    alias:
      "list_contact_methods_api_v1_organizations__org_id__patients__patient_id__contact_methods_get",
    description: `List all contact methods for a patient.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.array(ContactMethodRead),
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/contact-methods",
    alias:
      "create_contact_method_api_v1_organizations__org_id__patients__patient_id__contact_methods_post",
    description: `Add a new contact method to a patient.
If is_primary&#x3D;True, unsets other primaries of the same type.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ContactMethodCreate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ContactMethodRead,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/contact-methods/:contact_id",
    alias:
      "update_contact_method_api_v1_organizations__org_id__patients__patient_id__contact_methods__contact_id__patch",
    description: `Update a contact method.
If is_primary becomes True, unsets other primaries of the same type.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ContactMethodUpdate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "contact_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ContactMethodRead,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/contact-methods/:contact_id",
    alias:
      "delete_contact_method_api_v1_organizations__org_id__patients__patient_id__contact_methods__contact_id__delete",
    description: `Delete a contact method.
Cannot delete the only primary contact of any type.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "contact_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.void(),
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/documents",
    alias:
      "list_documents_api_v1_organizations__org_id__patients__patient_id__documents_get",
    description: `List documents for a patient.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "document_type",
        type: "Query",
        schema: action_type,
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(50),
      },
      {
        name: "offset",
        type: "Query",
        schema: z.number().int().gte(0).optional().default(0),
      },
    ],
    response: PaginatedDocuments,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/documents/:document_id",
    alias:
      "delete_document_api_v1_organizations__org_id__patients__patient_id__documents__document_id__delete",
    description: `Soft delete a document.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "document_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.void(),
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/documents/:document_id/confirm",
    alias:
      "confirm_upload_api_v1_organizations__org_id__patients__patient_id__documents__document_id__confirm_post",
    description: `Confirm document upload completion.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "document_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: DocumentRead,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/documents/:document_id/download-url",
    alias:
      "get_download_url_api_v1_organizations__org_id__patients__patient_id__documents__document_id__download_url_get",
    description: `Generate presigned S3 URL for document download.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "document_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: DocumentDownloadResponse,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/documents/upload-url",
    alias:
      "create_upload_url_api_v1_organizations__org_id__patients__patient_id__documents_upload_url_post",
    description: `Generate presigned S3 URL for document upload.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DocumentUploadRequest,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: DocumentUploadResponse,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/proxies",
    alias:
      "list_patient_proxies_api_v1_organizations__org_id__patients__patient_id__proxies_get",
    description: `List all proxies assigned to a patient.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ProxyListResponse,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/proxies",
    alias:
      "assign_proxy_api_v1_organizations__org_id__patients__patient_id__proxies_post",
    description: `Assign a proxy to a patient by email.
If user exists, grants immediate access.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ProxyAssignmentCreate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ProxyAssignmentRead,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/proxies/:assignment_id",
    alias:
      "update_proxy_permissions_api_v1_organizations__org_id__patients__patient_id__proxies__assignment_id__patch",
    description: `Update proxy permissions.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ProxyAssignmentUpdate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "assignment_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ProxyAssignmentRead,
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
    path: "/api/v1/organizations/:org_id/patients/:patient_id/proxies/:assignment_id",
    alias:
      "revoke_proxy_api_v1_organizations__org_id__patients__patient_id__proxies__assignment_id__delete",
    description: `Revoke proxy access (soft delete with revoked_at).`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "assignment_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.void(),
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
    path: "/api/v1/organizations/:org_id/providers",
    alias: "create_provider_api_v1_organizations__org_id__providers_post",
    description: `Create a provider profile for a user (promotes user to provider role).
Requires admin access.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ProviderCreate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ProviderRead,
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
    path: "/api/v1/organizations/:org_id/providers",
    alias: "list_providers_api_v1_organizations__org_id__providers_get",
    description: `List all providers in the organization.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "specialty",
        type: "Query",
        schema: action_type,
      },
      {
        name: "is_active",
        type: "Query",
        schema: is_locked,
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(50),
      },
      {
        name: "offset",
        type: "Query",
        schema: z.number().int().gte(0).optional().default(0),
      },
    ],
    response: PaginatedProviders,
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
    path: "/api/v1/organizations/:org_id/providers/:provider_id",
    alias:
      "get_provider_api_v1_organizations__org_id__providers__provider_id__get",
    description: `Get full provider details.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "provider_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ProviderRead,
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
    path: "/api/v1/organizations/:org_id/providers/:provider_id",
    alias:
      "update_provider_api_v1_organizations__org_id__providers__provider_id__patch",
    description: `Update provider fields. Requires admin access.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ProviderUpdate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "provider_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ProviderRead,
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
    path: "/api/v1/organizations/:org_id/providers/:provider_id",
    alias:
      "delete_provider_api_v1_organizations__org_id__providers__provider_id__delete",
    description: `Soft delete a provider (set is_active&#x3D;false and deleted_at).
Requires admin access.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "provider_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.void(),
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
    path: "/api/v1/organizations/:org_id/staff",
    alias: "create_staff_api_v1_organizations__org_id__staff_post",
    description: `Create a staff profile for a user.
Requires admin access.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: StaffCreate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: StaffRead,
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
    path: "/api/v1/organizations/:org_id/staff",
    alias: "list_staff_api_v1_organizations__org_id__staff_get",
    description: `List all staff members in the organization.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "department",
        type: "Query",
        schema: action_type,
      },
      {
        name: "is_active",
        type: "Query",
        schema: is_locked,
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(50),
      },
      {
        name: "offset",
        type: "Query",
        schema: z.number().int().gte(0).optional().default(0),
      },
    ],
    response: PaginatedStaff,
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
    path: "/api/v1/organizations/:org_id/staff/:staff_id",
    alias: "get_staff_api_v1_organizations__org_id__staff__staff_id__get",
    description: `Get full staff details.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "staff_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: StaffRead,
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
    path: "/api/v1/organizations/:org_id/staff/:staff_id",
    alias: "update_staff_api_v1_organizations__org_id__staff__staff_id__patch",
    description: `Update staff fields. Requires admin access.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: StaffUpdate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "staff_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: StaffRead,
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
    path: "/api/v1/organizations/:org_id/staff/:staff_id",
    alias: "delete_staff_api_v1_organizations__org_id__staff__staff_id__delete",
    description: `Soft delete a staff member (set is_active&#x3D;false and deleted_at).
Requires admin access.`,
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "staff_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.void(),
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
    path: "/api/v1/organizations/:org_id/tasks/",
    alias: "list_org_tasks_api_v1_organizations__org_id__tasks__get",
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "status",
        type: "Query",
        schema: action_type,
      },
      {
        name: "assignee_id",
        type: "Query",
        schema: action_type,
      },
      {
        name: "priority",
        type: "Query",
        schema: action_type,
      },
      {
        name: "skip",
        type: "Query",
        schema: z.number().int().optional().default(0),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
    ],
    response: z.array(TaskRead),
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
    path: "/api/v1/organizations/:org_id/tasks/",
    alias: "create_task_api_v1_organizations__org_id__tasks__post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TaskCreate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: TaskRead,
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
    path: "/api/v1/organizations/:org_id/tasks/:task_id",
    alias: "update_task_api_v1_organizations__org_id__tasks__task_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TaskUpdate,
      },
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "task_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: TaskRead,
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
    path: "/api/v1/organizations/:org_id/tasks/:task_id",
    alias: "delete_task_api_v1_organizations__org_id__tasks__task_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "org_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "task_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.void(),
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
    path: "/api/v1/support/admin/tickets",
    alias: "get_all_tickets_api_v1_support_admin_tickets_get",
    description: `Admin: List all tickets with optional filtering.`,
    requestFormat: "json",
    parameters: [
      {
        name: "status",
        type: "Query",
        schema: action_type,
      },
      {
        name: "assigned_to_me",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.array(TicketRead),
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
    path: "/api/v1/support/admin/tickets/:ticket_id",
    alias:
      "update_ticket_status_api_v1_support_admin_tickets__ticket_id__patch",
    description: `Admin: Update ticket status, priority, or assignment.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TicketUpdate,
      },
      {
        name: "ticket_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: TicketRead,
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
    path: "/api/v1/support/admin/tickets/:ticket_id/assign",
    alias:
      "assign_ticket_api_v1_support_admin_tickets__ticket_id__assign_patch",
    description: `Admin: Assign ticket to a user (staff).`,
    requestFormat: "json",
    parameters: [
      {
        name: "ticket_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "assignee_id",
        type: "Query",
        schema: z.string().uuid(),
      },
    ],
    response: TicketRead,
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
    path: "/api/v1/support/tickets",
    alias: "get_my_tickets_api_v1_support_tickets_get",
    description: `List user&#x27;s support tickets.`,
    requestFormat: "json",
    response: z.array(TicketRead),
  },
  {
    method: "post",
    path: "/api/v1/support/tickets",
    alias: "create_ticket_api_v1_support_tickets_post",
    description: `Create a new support ticket with an initial message.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TicketCreate,
      },
    ],
    response: TicketRead,
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
    path: "/api/v1/support/tickets/:ticket_id",
    alias: "get_ticket_api_v1_support_tickets__ticket_id__get",
    description: `Get a specific ticket with messages.`,
    requestFormat: "json",
    parameters: [
      {
        name: "ticket_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: TicketRead,
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
    path: "/api/v1/support/tickets/:ticket_id/messages",
    alias: "add_message_api_v1_support_tickets__ticket_id__messages_post",
    description: `Add a message to a ticket.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SupportMessageCreate,
      },
      {
        name: "ticket_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: SupportMessageRead,
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
    path: "/api/v1/users/me/notifications",
    alias: "list_notifications_api_v1_users_me_notifications_get",
    description: `List notifications for the current user.`,
    requestFormat: "json",
    parameters: [
      {
        name: "page",
        type: "Query",
        schema: z.number().int().gte(1).optional().default(1),
      },
      {
        name: "size",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(20),
      },
      {
        name: "is_read",
        type: "Query",
        schema: is_locked,
      },
      {
        name: "type",
        type: "Query",
        schema: action_type,
      },
    ],
    response: NotificationListResponse,
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
    path: "/api/v1/users/me/notifications/:notification_id",
    alias:
      "delete_notification_api_v1_users_me_notifications__notification_id__delete",
    description: `Delete a notification.`,
    requestFormat: "json",
    parameters: [
      {
        name: "notification_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.void(),
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
    path: "/api/v1/users/me/notifications/:notification_id/read",
    alias:
      "mark_as_read_api_v1_users_me_notifications__notification_id__read_patch",
    description: `Mark a notification as read.`,
    requestFormat: "json",
    parameters: [
      {
        name: "notification_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: NotificationRead,
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
    path: "/api/v1/users/me/notifications/:notification_id/unread",
    alias:
      "mark_as_unread_api_v1_users_me_notifications__notification_id__unread_patch",
    description: `Mark a notification as unread.`,
    requestFormat: "json",
    parameters: [
      {
        name: "notification_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: NotificationRead,
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
    path: "/api/v1/users/me/notifications/mark-all-read",
    alias: "mark_all_read_api_v1_users_me_notifications_mark_all_read_post",
    description: `Mark all notifications as read for the current user.`,
    requestFormat: "json",
    response: z.void(),
  },
  {
    method: "get",
    path: "/api/v1/users/me/notifications/unread-count",
    alias: "get_unread_count_api_v1_users_me_notifications_unread_count_get",
    description: `Get the number of unread notifications.`,
    requestFormat: "json",
    response: z.object({ count: z.number().int() }).passthrough(),
  },
  {
    method: "get",
    path: "/api/v1/users/me/proxy",
    alias: "get_my_proxy_profile_api_v1_users_me_proxy_get",
    description: `Get the current user&#x27;s proxy profile if they are a proxy.
Returns None if the user is not a proxy.`,
    requestFormat: "json",
    response: z.union([ProxyProfileRead, z.null()]),
  },
  {
    method: "get",
    path: "/api/v1/users/me/proxy-patients",
    alias: "get_my_proxy_patients_api_v1_users_me_proxy_patients_get",
    description: `List patients the current user is proxy for.`,
    requestFormat: "json",
    response: z.array(ProxyPatientRead),
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
    method: "get",
    path: "/api/v1/users/me/threads",
    alias: "list_threads_api_v1_users_me_threads_get",
    description: `List message threads for the current user.`,
    requestFormat: "json",
    parameters: [
      {
        name: "page",
        type: "Query",
        schema: z.number().int().gte(1).optional().default(1),
      },
      {
        name: "size",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(20),
      },
    ],
    response: ThreadListResponse,
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
    path: "/api/v1/users/me/threads",
    alias: "create_thread_api_v1_users_me_threads_post",
    description: `Create a new message thread.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ThreadCreate,
      },
    ],
    response: ThreadRead,
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
    path: "/api/v1/users/me/threads/:thread_id",
    alias: "get_thread_api_v1_users_me_threads__thread_id__get",
    description: `Get thread details.`,
    requestFormat: "json",
    parameters: [
      {
        name: "thread_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ThreadDetail,
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
    path: "/api/v1/users/me/threads/:thread_id/messages",
    alias: "send_message_api_v1_users_me_threads__thread_id__messages_post",
    description: `Send a message to a thread.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ body: z.string() }).passthrough(),
      },
      {
        name: "thread_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: MessageRead,
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
    path: "/api/v1/users/me/threads/:thread_id/read",
    alias: "mark_read_api_v1_users_me_threads__thread_id__read_post",
    description: `Mark thread as read.`,
    requestFormat: "json",
    parameters: [
      {
        name: "thread_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.void(),
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
    path: "/api/v1/users/me/timezone",
    alias: "get_user_timezone_api_v1_users_me_timezone_get",
    description: `Get the current user&#x27;s effective timezone.

Resolution order:
1. User&#x27;s personal timezone preference (if set)
2. Organization&#x27;s timezone (if user has org membership)
3. Default timezone (America/New_York)

Returns timezone string and source indicator.`,
    requestFormat: "json",
    response: TimezoneResponse,
  },
  {
    method: "delete",
    path: "/api/v1/users/me/timezone",
    alias: "clear_user_timezone_api_v1_users_me_timezone_delete",
    description: `Clear the user&#x27;s timezone preference to use organization default.`,
    requestFormat: "json",
    response: TimezoneResponse,
  },
  {
    method: "patch",
    path: "/api/v1/users/me/timezone",
    alias: "update_user_timezone_api_v1_users_me_timezone_patch",
    description: `Update the current user&#x27;s timezone preference.

Set to a valid IANA timezone identifier to override organization default.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ timezone: z.string() }).passthrough(),
      },
    ],
    response: TimezoneResponse,
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
    path: "/api/v1/users/tasks/me/all",
    alias: "list_my_tasks_api_v1_users_tasks_me_all_get",
    description: `Get all tasks assigned to current user across all organizations`,
    requestFormat: "json",
    parameters: [
      {
        name: "status",
        type: "Query",
        schema: action_type,
      },
      {
        name: "skip",
        type: "Query",
        schema: z.number().int().optional().default(0),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
    ],
    response: z.array(TaskRead),
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
