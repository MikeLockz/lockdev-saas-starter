# Story 17.2: Call Center & Task API
**User Story:** As a Call Center Agent, I want to log calls and manage tasks.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 5.2 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Call Center")

## Technical Specification
**Goal:** Implement call logging and task management APIs.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/operations.py` (NEW)
    - `CallCreate` (patient_id, direction, phone_number)
    - `CallUpdate` (status, notes, outcome)
    - `CallRead` (all fields + patient/agent names)
    - `TaskCreate` (title, description, assignee_id, priority, due_date)
    - `TaskUpdate` (status, priority, due_date)
    - `TaskRead` (all fields)

2.  **API Router:** `backend/src/api/calls.py` (NEW)
    - `GET /api/v1/organizations/{org_id}/calls`
      - List calls with filters (status, agent, date)
      - Default: today's calls
    - `POST /api/v1/organizations/{org_id}/calls`
      - Log new call (starts timer)
    - `PATCH /api/v1/organizations/{org_id}/calls/{call_id}`
      - Update status, notes, outcome
      - Set ended_at on COMPLETED

3.  **API Router:** `backend/src/api/tasks.py` (NEW)
    - `GET /api/v1/organizations/{org_id}/tasks`
      - List tasks (filter by assignee, status, priority)
    - `GET /api/v1/users/me/tasks`
      - My assigned tasks
    - `POST /api/v1/organizations/{org_id}/tasks`
      - Create task
    - `PATCH /api/v1/organizations/{org_id}/tasks/{task_id}`
      - Update task (status, priority, reassign)
    - `DELETE /api/v1/organizations/{org_id}/tasks/{task_id}`
      - Cancel/delete task

## Acceptance Criteria
- [ ] `POST /calls` creates call record.
- [ ] Call status workflow works.
- [ ] Task CRUD fully functional.
- [ ] My tasks returns assigned tasks.
- [ ] Filters work correctly.
- [ ] Audit log captures operations.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_calls.py`
- `pytest tests/api/test_tasks.py`

**Manual Verification:**
- Log call, update to completed.
- Create and complete a task.
