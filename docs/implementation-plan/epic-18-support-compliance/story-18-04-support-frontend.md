# Story 18.4: Support & Compliance Frontend
**User Story:** As a User, I want a support form, and as an Auditor, I want an audit log viewer.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 5.3 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Routes: `/help`, `/admin/audit-logs`)

## Technical Specification
**Goal:** Implement support ticket UI and audit log viewer.

**Changes Required:**

1.  **Routes:** `frontend/src/routes/_auth/`
    - `help/index.tsx` - Help center landing
    - `help/contact.tsx` - Support ticket form
    - `help/tickets.tsx` - My tickets list
    - `help/tickets/$ticketId.tsx` - Ticket detail
    - `admin/audit-logs.tsx` - Audit log viewer

2.  **Components:** `frontend/src/components/support/`
    - `SupportTicketForm.tsx`
      - Subject, category, priority
      - Message body
    - `TicketList.tsx`
      - User's tickets with status badges
    - `TicketDetail.tsx`
      - Conversation thread
      - Reply form

3.  **Components:** `frontend/src/components/admin/`
    - `AuditLogViewer.tsx`
      - Search filters
      - Results table
      - Export button
    - `AuditLogFilters.tsx`
      - Date picker, resource type select
      - Action type, user search
    - `ImpersonationBanner.tsx`
      - Shows when impersonating
      - Exit impersonation button

4.  **Hooks:** `frontend/src/hooks/api/`
    - `useSupportTickets.ts`
    - `useAuditLogs.ts`

## Acceptance Criteria
- [ ] `/help/contact` shows support form.
- [ ] `/help/tickets` shows user's tickets.
- [ ] Ticket detail shows conversation.
- [ ] `/admin/audit-logs` has search filters.
- [ ] Audit log table displays results.
- [ ] CSV export works.

## Verification Plan
**Automated Tests:**
- `pnpm test -- SupportTicketForm`
- `pnpm test -- AuditLogViewer`

**Manual Verification:**
- Submit support ticket, view in list.
- Search audit logs with filters.
