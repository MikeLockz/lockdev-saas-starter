# Story 8.4: Invitation UI
**User Story:** As an Admin, I want a UI to invite members, and as an Invitee, I want to accept invitations easily.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 1.3 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Routes: /invite/:token, /admin/members)

## Technical Specification
**Goal:** Implement invitation modal and acceptance flow UI.

**Changes Required:**

1.  **Routes:** `frontend/src/routes/`
    - `invite.$token.tsx` - Public route for accepting invites
      - Fetches invite details by token
      - Shows org name, role offered
      - "Accept" button (requires login first)
    - `_auth/admin/members.tsx` - Members management page
      - MemberTable + Invite button

2.  **Components:** `frontend/src/components/org/`
    - `InviteModal.tsx`
      - Email input
      - Role select (STAFF, PROVIDER, ADMIN)
      - Submit triggers API call
    - `InviteAccept.tsx`
      - Displays invite details
      - Accept/Decline buttons

3.  **Hooks:** `frontend/src/hooks/`
    - `useInvitation.ts` - Query for invite by token
    - `useAcceptInvitation.ts` - Mutation to accept
    - `useCreateInvitation.ts` - Mutation to create invite

4.  **Flow:**
    - Admin clicks "Invite" → Modal opens
    - Enter email, select role → Submit
    - Invitee clicks email link → `/invite/:token`
    - If not logged in → Redirect to login with `returnTo`
    - After login → Accept invite → Redirect to dashboard

## Acceptance Criteria
- [x] `/admin/members` shows member list with Invite button.
- [x] InviteModal validates email format.
- [x] Successful invite shows success toast.
- [x] `/invite/:token` displays org and role.
- [x] Accepting adds user to org and redirects.
- [x] Invalid/expired token shows error.

## Verification Plan
**Automated Tests:**
- `pnpm test -- InviteModal` (component test)
- Playwright E2E: Invite flow (if time permits)

**Manual Verification:**
- As admin, invite a new email.
- Check Mailpit for email.
- Click link, login/signup, accept invite.
- Verify membership in member table.
