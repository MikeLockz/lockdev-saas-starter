# Story 4.4: Background Worker (ARQ)
**User Story:** As a Developer, I want to run long-running tasks in the background, so that the API remains responsive.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 4.4 from `docs/03`

## Technical Specification
**Goal:** Configure `arq` worker with Redis.

**Changes Required:**
1.  **File:** `backend/src/worker.py`
    - `WorkerSettings`.
    - `on_startup` (DB/Redis connect).
    - `functions` list.
2.  **Task:** Implement `health_check_task` as a proof of concept.

## Acceptance Criteria
- [ ] Worker starts successfully.
- [ ] Can enqueue and execute a task.

## Verification Plan
**Manual Verification:**
- Start worker. Enqueue task via REPL. Check logs for completion.
