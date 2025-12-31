-- Enable UUID extension for secure, non-sequential IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Enable pg_trgm for efficient text search (ILIKE)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ==========================================
-- 1. IDENTITY & TENANCY (Core)
-- ==========================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    is_super_admin BOOLEAN DEFAULT FALSE, -- Platform owner access
    mfa_enabled BOOLEAN DEFAULT FALSE,
    transactional_consent BOOLEAN DEFAULT TRUE, -- TCPA Compliance
    marketing_consent BOOLEAN DEFAULT FALSE,
    requires_consent BOOLEAN DEFAULT TRUE, -- Cache flag for mandatory consents
    last_login_at TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE -- Soft delete support
);

CREATE TABLE user_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    fcm_token VARCHAR(512) NOT NULL,
    platform VARCHAR(20), -- 'ios', 'android', 'web'
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, fcm_token)
);

CREATE TABLE user_mfa_backup_codes (
    user_id UUID NOT NULL REFERENCES users(id),
    code_hash VARCHAR(255) NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, code_hash)
);

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    tax_id VARCHAR(50), -- EIN for billing
    settings_json JSONB DEFAULT '{}', -- Tenant specific configs (logo, colors)
    stripe_customer_id VARCHAR(100), -- External Billing ID
    subscription_status VARCHAR(50) DEFAULT 'INCOMPLETE', -- 'ACTIVE', 'PAST_DUE', 'CANCELED'
    member_count INTEGER DEFAULT 0, -- Cached count
    patient_count INTEGER DEFAULT 0, -- Cached count
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE -- Soft delete support
);

-- "Organization_Member" - Links a User to an Org (Many-to-Many)
CREATE TABLE organization_memberships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    user_id UUID NOT NULL REFERENCES users(id),
    role VARCHAR(50) NOT NULL, -- 'PROVIDER', 'STAFF', 'ADMIN'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE, -- Soft delete support
    UNIQUE(organization_id, user_id)
);

CREATE TABLE invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING', -- 'PENDING', 'ACCEPTED', 'DECLINED', 'EXPIRED'
    inviter_user_id UUID REFERENCES users(id),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resend_count INTEGER DEFAULT 0
);

-- ==========================================
-- 2. ROLE PROFILES
-- ==========================================

-- A User who is a Clinical Provider
CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    npi_number VARCHAR(10) UNIQUE, -- National Provider Identifier
    dea_number VARCHAR(20), -- Controlled substance license
    specialty VARCHAR(100),
    state_licenses JSONB DEFAULT '[]', -- Array of {state, license_number, expiry}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- A User who is non-clinical Staff
CREATE TABLE staff (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    employee_id VARCHAR(50),
    job_title VARCHAR(100), -- 'Medical Assistant', 'Biller'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- The Patient Entity (Receiver of Care)
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id), -- NULL if dependent/minor
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    medical_record_number VARCHAR(100), -- Internal MRN
    legal_sex VARCHAR(20),
    stripe_customer_id VARCHAR(100), -- For per-patient subscription
    subscription_status VARCHAR(50) DEFAULT 'INCOMPLETE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- The Proxy Entity (Manager of Care)
CREATE TABLE proxies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    relationship_to_patient VARCHAR(100), -- Generic default
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ==========================================
-- 3. CONTACT & PRIVACY (Critical for Safety)
-- ==========================================

CREATE TABLE contact_methods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id),
    type VARCHAR(20) NOT NULL, -- 'MOBILE', 'HOME', 'EMAIL'
    value VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    is_safe_for_voicemail BOOLEAN DEFAULT FALSE, -- SAFETY CRITICAL
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 4. RELATIONSHIPS & PERMISSIONS
-- ==========================================

-- Links Proxies to Patients with GRANULAR permissions
CREATE TABLE patient_proxy_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proxy_id UUID NOT NULL REFERENCES proxies(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    relationship_type VARCHAR(50) NOT NULL, -- 'PARENT', 'POA', 'GUARDIAN'
    
    -- Granular Permissions (Booleans or Bitmap)
    can_view_clinical_notes BOOLEAN DEFAULT FALSE,
    can_view_billing BOOLEAN DEFAULT TRUE,
    can_schedule_appointments BOOLEAN DEFAULT TRUE,
    
    access_granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE, -- For temporary guardianships
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE, -- For revocation history
    UNIQUE(proxy_id, patient_id)
);

-- Links Patients to Orgs (A patient can be at multiple clinics)
CREATE TABLE organization_patients (
    organization_id UUID NOT NULL REFERENCES organizations(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    status VARCHAR(50) DEFAULT 'ACTIVE', -- 'ACTIVE', 'DISCHARGED'
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    discharged_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (organization_id, patient_id)
);

-- Links Providers to Patients (Care Team)
CREATE TABLE care_team_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    provider_id UUID NOT NULL REFERENCES providers(id),
    is_primary_provider BOOLEAN DEFAULT FALSE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 5. COMPLIANCE & AUDITING (HIPAA)
-- ==========================================

-- Immutable Audit Log - NEVER DELETE ROWS FROM THIS TABLE
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_user_id UUID REFERENCES users(id), -- Who did it?
    organization_id UUID REFERENCES organizations(id), -- Where?
    
    resource_type VARCHAR(50) NOT NULL, -- 'PATIENT', 'NOTE', 'RX'
    resource_id UUID NOT NULL, -- The ID of the record accessed
    
    action_type VARCHAR(20) NOT NULL, -- 'READ', 'CREATE', 'UPDATE', 'DELETE'
    ip_address INET,
    user_agent TEXT,
    impersonator_id UUID REFERENCES users(id), -- If act_as was used
    
    -- Capture the delta for updates (what changed?)
    changes_json JSONB, 
    
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Track Patient Consents (HIPAA, Terms of Service)
CREATE TABLE consents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id),
    consent_type VARCHAR(50) NOT NULL, -- 'HIPAA_NOTICE', 'TREATMENT_AGREEMENT'
    agreed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    version_string VARCHAR(20) -- e.g., 'v1.2'
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id), -- Optional context
    type VARCHAR(50) NOT NULL, -- 'APPOINTMENT', 'MESSAGE', 'SYSTEM'
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    metadata_json JSONB DEFAULT '{}', -- Links to resource
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE -- Soft delete support
);

-- ==========================================
-- 6. SCHEDULING & APPOINTMENTS
-- ==========================================

CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    provider_id UUID NOT NULL REFERENCES providers(id),
    
    appointment_type VARCHAR(50) NOT NULL, -- 'IN_PERSON', 'TELEHEALTH'
    status VARCHAR(50) DEFAULT 'SCHEDULED', -- 'SCHEDULED', 'CONFIRMED', 'COMPLETED', 'CANCELLED', 'NO_SHOW'
    
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    
    reason TEXT,
    notes TEXT,
    location VARCHAR(255), -- Room number or link
    
    telehealth_url TEXT,
    
    cancellation_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for Appointments
CREATE INDEX idx_appointments_org ON appointments(organization_id);
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_provider ON appointments(provider_id);
CREATE INDEX idx_appointments_date ON appointments(scheduled_at);
CREATE INDEX idx_appointments_composite ON appointments(organization_id, scheduled_at);
CREATE INDEX idx_appointments_status ON appointments(status);

-- ==========================================
-- 7. MESSAGING (Secure Provider-Patient)
-- ==========================================

CREATE TABLE message_threads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    patient_id UUID NOT NULL REFERENCES patients(id), -- Context of the thread
    
    subject VARCHAR(255),
    is_archived BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Bumped on new message
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE message_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id UUID NOT NULL REFERENCES message_threads(id),
    user_id UUID NOT NULL REFERENCES users(id),
    
    last_read_at TIMESTAMP WITH TIME ZONE,
    
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id UUID NOT NULL REFERENCES message_threads(id),
    sender_id UUID NOT NULL REFERENCES users(id),
    
    body TEXT NOT NULL,
    attachments_json JSONB DEFAULT '[]', -- Array of Document IDs
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Messaging
CREATE INDEX idx_threads_org ON message_threads(organization_id);
CREATE INDEX idx_threads_patient ON message_threads(patient_id);
CREATE INDEX idx_participants_user ON message_participants(user_id);
CREATE INDEX idx_messages_thread ON messages(thread_id);
CREATE INDEX idx_messages_thread_created ON messages(thread_id, created_at DESC); -- Optimization for "last message"

-- ==========================================
-- 8. DOCUMENTS & FILES
-- ==========================================

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    uploaded_by UUID REFERENCES users(id),
    
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(512) NOT NULL,
    content_type VARCHAR(100),
    size_bytes BIGINT,
    
    scan_status VARCHAR(50) DEFAULT 'PENDING', -- 'PENDING', 'CLEAN', 'INFECTED'
    processing_status VARCHAR(50) DEFAULT 'PENDING', -- 'OCR_PROCESSING', 'COMPLETED'
    
    description TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE -- Soft delete
);

-- Indexes for Documents
CREATE INDEX idx_documents_org ON documents(organization_id);
CREATE INDEX idx_documents_patient ON documents(patient_id);
CREATE INDEX idx_documents_content_type ON documents(content_type);

-- ==========================================
-- 9. CALL CENTER
-- ==========================================

CREATE TABLE calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    patient_id UUID REFERENCES patients(id), -- Nullable if unknown caller initially
    agent_id UUID REFERENCES users(id), -- Null if in queue
    
    caller_id VARCHAR(50),
    call_type VARCHAR(20) NOT NULL, -- 'INBOUND', 'OUTBOUND'
    status VARCHAR(50) NOT NULL, -- 'QUEUED', 'IN_PROGRESS', 'COMPLETED', 'VOICEMAIL', 'MISSED'
    outcome VARCHAR(50), -- 'RESOLVED', 'SCHEDULED_APPOINTMENT', etc.
    
    duration_seconds INTEGER DEFAULT 0,
    wait_time_seconds INTEGER DEFAULT 0,
    
    recording_url TEXT,
    notes TEXT,
    
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    entered_queue_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    assignee_id UUID REFERENCES users(id),
    created_by UUID REFERENCES users(id),
    
    related_resource_type VARCHAR(50), -- 'CALL', 'PATIENT'
    related_resource_id UUID,
    
    description TEXT NOT NULL,
    due_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'PENDING', -- 'PENDING', 'COMPLETED', 'CANCELLED'
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for Call Center
CREATE INDEX idx_calls_org_status ON calls(organization_id, status);
CREATE INDEX idx_calls_patient ON calls(patient_id);
CREATE INDEX idx_calls_agent ON calls(agent_id);
CREATE INDEX idx_calls_queue_order ON calls(entered_queue_at ASC) WHERE status = 'QUEUED';
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);

-- ==========================================
-- 10. SUPPORT
-- ==========================================

CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id), -- Context
    
    ticket_number SERIAL, -- User friendly ID (e.g. 1045)
    category VARCHAR(50),
    subject VARCHAR(255),
    body TEXT,
    status VARCHAR(50) DEFAULT 'OPEN', -- 'OPEN', 'IN_PROGRESS', 'RESOLVED'
    urgency VARCHAR(20) DEFAULT 'NORMAL',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE support_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES support_tickets(id),
    sender_id UUID REFERENCES users(id), -- Null if system
    
    body TEXT NOT NULL,
    is_internal_note BOOLEAN DEFAULT FALSE,
    attachment_document_id UUID,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 11. PERFORMANCE INDEXES (Optimizations)
-- ==========================================

-- Standard Foreign Key Indexes (Postgres doesn't auto-index FKs)
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_deleted ON users(deleted_at);
CREATE INDEX idx_org_members_user ON organization_memberships(user_id);
CREATE INDEX idx_org_members_role ON organization_memberships(organization_id, role);
CREATE INDEX idx_organization_patients_lookup ON organization_patients(organization_id, patient_id);
CREATE INDEX idx_organization_patients_reverse ON organization_patients(patient_id, organization_id);
CREATE INDEX idx_patients_mrn ON patients(medical_record_number);

-- Trigram Indexes for Fuzzy Search (Requires pg_trgm)
CREATE INDEX idx_patients_last_name_trgm ON patients USING gin (last_name gin_trgm_ops);
CREATE INDEX idx_patients_first_name_trgm ON patients USING gin (first_name gin_trgm_ops);
CREATE INDEX idx_patients_mrn_trgm ON patients USING gin (medical_record_number gin_trgm_ops);

CREATE INDEX idx_proxies_user ON proxies(user_id);
CREATE INDEX idx_audit_resource ON audit_logs(resource_id);
CREATE INDEX idx_audit_actor ON audit_logs(actor_user_id);
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);

-- Indexes for Admin & Support Performance
CREATE INDEX idx_audit_logs_org_date ON audit_logs(organization_id, occurred_at DESC);
CREATE INDEX idx_support_tickets_user ON support_tickets(user_id);
CREATE INDEX idx_notifications_created ON notifications(user_id, created_at DESC);

-- ==========================================
-- 12. TELEMETRY
-- ==========================================

CREATE TABLE telemetry_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    event_name VARCHAR(100) NOT NULL,
    properties JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Optimization for message thread listing
CREATE INDEX idx_threads_org_updated ON message_threads(organization_id, updated_at DESC);
CREATE INDEX idx_support_messages_ticket ON support_messages(ticket_id);