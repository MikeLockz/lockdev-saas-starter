# Story 21.4: Proxy Patient Access Flow
**User Story:** As a Proxy, I want to access patients assigned to me, so that I can manage their care on their behalf.

## Status
- [x] **Done** (Implemented in Epic 14)

## Context
- **Related:** `epic-14-proxies/story-14-02-proxy-api.md`
- **API Ref:** `GET /users/me/proxy-patients`

## Technical Specification
**Goal:** Verify proxy access to patient data through assignment flow.

**Existing Implementation:**
1. Admin assigns proxy to patient via `PatientProxyAssignment`
2. Proxy gains access to patient data based on `permissions_json`
3. Proxy can view patient via `/users/me/proxy-patients`

**Organization Association:**
- Proxy → Patient → OrganizationPatient → Organization
- Proxy accesses patient data within patient's org context
- No direct `Proxy.organization_id` (access is per-patient)

**Gap Analysis:**
- Current implementation: ✅ Working
- Enhancement needed: Proxy should see org name for each patient

## Acceptance Criteria
- [x] Proxy assignment creates PatientProxyAssignment.
- [x] Proxy can list their assigned patients.
- [x] Proxy permissions are respected (view records, manage appointments, etc.).
- [ ] Proxy sees organization name for each managed patient (ENHANCEMENT).

## Verification Plan
**Manual Verification:**
- Create proxy user, assign to patient, verify access controls work.
