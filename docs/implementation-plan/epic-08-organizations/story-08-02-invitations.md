# Story 8.2: Invitation Flow
**User Story:** As an Organization Admin, I want to invite team members by email, so that they can join my organization.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 1.3 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Invitations")
- **DDL Ref:** `docs/04 - sql.ddl` (invitations table)

## Technical Specification
**Goal:** Implement invitation creation, email sending, and acceptance flow.

**Changes Required:**

1.  **Migration:** `backend/migrations/versions/xxx_invitations.py`
    - Create `invitations` table:
      - `id` (UUID, PK)
      - `organization_id` (FK to organizations)
      - `email` (String, invitee email)
      - `role` (String: PROVIDER, STAFF, ADMIN)
      - `token` (String, unique, URL-safe)
      - `invited_by_user_id` (FK to users)
      - `status` (String: PENDING, ACCEPTED, EXPIRED)
      - `created_at`, `expires_at`, `accepted_at`

2.  **Model:** `backend/src/models/invitations.py` (NEW)
    - `Invitation` SQLAlchemy model

3.  **Schemas:** `backend/src/schemas/invitations.py` (NEW)
    - `InvitationCreate` (email, role)
    - `InvitationRead` (id, email, role, status, created_at, expires_at)

4.  **Endpoints:** `backend/src/api/organizations.py`
    - `POST /api/v1/organizations/{org_id}/invitations` - Send invite
      - Generate secure token
      - Create invitation record
      - Queue email via worker
    - `GET /api/v1/organizations/{org_id}/invitations` - List pending invites

5.  **Endpoints:** `backend/src/api/invitations.py` (NEW)
    - `GET /api/v1/invitations/{token}` - Get invite details (public)
    - `POST /api/v1/invitations/{token}/accept` - Accept invitation
      - Requires authentication
      - Creates OrganizationMember
      - Updates invitation status

6.  **Worker Task:** `backend/src/worker.py`
    - `send_invitation_email` task
      - Uses email template with accept URL

## Acceptance Criteria
- [x] `POST /invitations` creates invitation and queues email.
- [x] Invitation email contains accept link with token.
- [x] `GET /invitations/{token}` returns invite details (org name, role).
- [x] `POST /invitations/{token}/accept` adds user to org.
- [x] Existing org member cannot be re-invited.
- [x] Expired invitations return 410 Gone.
- [x] Audit log captures invite sent and accepted.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_invitations.py::test_create_invitation`
- `pytest tests/api/test_invitations.py::test_accept_invitation`
- `pytest tests/api/test_invitations.py::test_expired_invitation`

**Manual Verification:**
- Invite user, check Mailpit for email.
- Click link, log in, verify membership created.
