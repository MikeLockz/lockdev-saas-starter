-- Enable UUID extension for secure, non-sequential IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 1. IDENTITY & TENANCY (Core)
-- ==========================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_super_admin BOOLEAN DEFAULT FALSE, -- Platform owner access
    mfa_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE -- Soft delete support
);

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    tax_id VARCHAR(50), -- EIN for billing
    settings_json JSONB DEFAULT '{}', -- Tenant specific configs (logo, colors)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- "Organization_Member" - Links a User to an Org (Many-to-Many)
CREATE TABLE organization_memberships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    user_id UUID NOT NULL REFERENCES users(id),
    role VARCHAR(50) NOT NULL, -- 'PROVIDER', 'STAFF', 'ADMIN'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, user_id)
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- A User who is non-clinical Staff
CREATE TABLE staff (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    employee_id VARCHAR(50),
    job_title VARCHAR(100), -- 'Medical Assistant', 'Biller'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- The Proxy Entity (Manager of Care)
CREATE TABLE proxies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    relationship_to_patient VARCHAR(100), -- Generic default
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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
    UNIQUE(proxy_id, patient_id)
);

-- Links Patients to Orgs (A patient can be at multiple clinics)
CREATE TABLE organization_patients (
    organization_id UUID NOT NULL REFERENCES organizations(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    status VARCHAR(50) DEFAULT 'ACTIVE', -- 'ACTIVE', 'DISCHARGED'
    PRIMARY KEY (organization_id, patient_id)
);

-- Links Providers to Patients (Care Team)
CREATE TABLE care_team_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    provider_id UUID NOT NULL REFERENCES providers(id),
    is_primary_provider BOOLEAN DEFAULT FALSE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- CRITICAL CONSTRAINT: Enforce "One Primary Provider" business rule
-- Only ONE provider can be marked as primary per patient per organization
-- Implemented via partial unique index (only applies where is_primary_provider=TRUE)
-- See migration: 20260114_add_unique_primary_provider_constraint.py
CREATE UNIQUE INDEX idx_unique_primary_provider_per_patient
ON care_team_assignments (organization_id, patient_id)
WHERE is_primary_provider = TRUE;

COMMENT ON INDEX idx_unique_primary_provider_per_patient IS
'Enforces business rule: Only ONE provider can be primary per patient per organization. Partial index only applies where is_primary_provider=TRUE.';

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