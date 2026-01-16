# Story 18.2: Support Ticket API
**User Story:** As a User, I want to create and track support tickets.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 5.3 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Support")

## Technical Specification
**Goal:** Implement support ticket CRUD and messaging.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/support.py` (NEW)
    - `TicketCreate` (subject, category, priority, initial_message)
    - `TicketRead` (all fields + message count)
    - `TicketUpdate` (status, priority, assigned_to_id)
    - `SupportMessageCreate` (body, is_internal)
    - `SupportMessageRead` (all fields)

2.  **API Router:** `backend/src/api/support.py` (NEW)
    - `GET /api/v1/support/tickets`
      - List user's tickets
    - `POST /api/v1/support/tickets`
      - Create ticket with initial message
    - `GET /api/v1/support/tickets/{ticket_id}`
      - Get ticket with messages
    - `POST /api/v1/support/tickets/{ticket_id}/messages`
      - Add message to ticket
    - `PATCH /api/v1/support/tickets/{ticket_id}`
      - Update status (staff only)

3.  **Staff Routes:**
    - `GET /api/v1/admin/support/tickets`
      - All tickets (staff view)
      - Filter by status, assignee
    - `PATCH /api/v1/admin/support/tickets/{id}/assign`
      - Assign to agent

## Acceptance Criteria
- [ ] `POST /support/tickets` creates ticket.
- [ ] User sees only their tickets.
- [ ] Staff sees all tickets.
- [ ] Messages added to ticket.
- [ ] Internal messages hidden from user.
- [ ] Assignment and status updates work.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_support.py`

**Manual Verification:**
- Create ticket as user.
- Respond as staff with internal note.
