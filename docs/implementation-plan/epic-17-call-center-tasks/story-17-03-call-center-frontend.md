# Story 17.3: Call Center Frontend
**User Story:** As a Call Center Agent, I want a dashboard to manage calls and tasks.

## Status
- [x] **Completed**

## Context
- **Roadmap Ref:** Step 5.2 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Route: `/call-center`)

## Technical Specification
**Goal:** Implement call center dashboard and task board.

**Changes Required:**

1.  **Routes:** `frontend/src/routes/_auth/`
    - `call-center/index.tsx` - Call center dashboard
    - `tasks/index.tsx` - Task board

2.  **Components:** `frontend/src/components/calls/`
    - `CallCenterDashboard.tsx`
      - Call queue panel
      - Active call panel
      - Recent calls list
    - `CallCard.tsx`
      - Patient info, duration, status
      - Action buttons (answer, complete, transfer)
    - `CallLogForm.tsx`
      - Notes, outcome selection
    - `CallQueue.tsx`
      - Incoming/queued calls

3.  **Components:** `frontend/src/components/tasks/`
    - `TaskBoard.tsx`
      - Kanban-style or list view
      - Columns: TODO, IN_PROGRESS, DONE
      - Drag-and-drop (optional)
    - `TaskCard.tsx`
      - Title, priority badge, due date
      - Assignee avatar
    - `TaskCreateModal.tsx`
      - Full task creation form
    - `TaskDetail.tsx`
      - Full task view with history

4.  **Hooks:** `frontend/src/hooks/api/`
    - `useCalls.ts` - Call queue and history
    - `useTasks.ts` - Task list
    - `useMyTasks.ts` - Personal tasks

## Acceptance Criteria
- [x] `/call-center` shows call queue.
- [x] Can log and complete calls.
- [x] `/tasks` shows task board.
- [x] Can create, update, complete tasks.
- [x] Priority badges color-coded.
- [x] Due date warnings displayed.

## Verification Plan
**Automated Tests:**
- `pnpm test -- CallCenterDashboard`
- `pnpm test -- TaskBoard`

**Manual Verification:**
- Log a call, add notes, complete it.
- Create task, drag to done.
