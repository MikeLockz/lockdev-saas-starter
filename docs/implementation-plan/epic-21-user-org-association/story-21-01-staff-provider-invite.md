# Story 21.1: Staff/Provider Invitation Flow (Verification)
**User Story:** As an Organization Admin, I want to invite staff and providers by email, so that they can join my organization with the correct role.

## Status
- [x] **Done** (Implemented in Epic 8)

## Context
- **Related:** `epic-08-organizations/story-08-02-invitations.md`
- **API Ref:** `POST /organizations/{org_id}/invitations`

## Technical Specification
**Goal:** Verify existing invitation flow works correctly for staff/provider association.

**Existing Implementation:**
1. Admin creates invite via `InviteModal` (email, role: STAFF/PROVIDER/ADMIN)
2. Backend creates `Invitation` record with unique token
3. Worker queues invitation email with link to `/invite/{token}`
4. User clicks link, signs up (if needed) with **same email**
5. User accepts invitation → `OrganizationMember` created
6. If role=PROVIDER, separate `Provider` profile must be created

**Gap Identified:**
- Provider invite creates `OrganizationMember` but **not** `Provider` profile
- Admin may need to separately create Provider profile after invite acceptance

## Acceptance Criteria
- [x] Staff can join org via invite and access staff features.
- [x] Provider can join org via invite.
- [ ] Provider profile auto-created on invite acceptance (ENHANCEMENT).
- [x] Invitation email contains correct `/invite/{token}` URL.

## Verification Plan
**Manual Verification:**
- Send invite with role=STAFF, verify acceptance creates membership.
- Send invite with role=PROVIDER, verify acceptance and profile creation.
