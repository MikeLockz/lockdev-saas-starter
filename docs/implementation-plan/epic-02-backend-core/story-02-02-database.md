# Story 2.2: Database Setup (Async SQLAlchemy)
**User Story:** As a Developer, I want an async database connection, so that the API remains performant under load.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 2.2 from `docs/03`

## Technical Specification
**Goal:** Configure `AsyncEngine` and `AsyncSession`.

**Changes Required:**
1.  **File:** `backend/src/database.py`
    - Create `AsyncEngine` using `create_async_engine`.
    - Create `sessionmaker` factory.
    - Implement `get_db` dependency.
    - **CRITICAL:** Add `after_begin` event listener to set RLS session variables (`app.current_user_id`, `app.current_tenant_id`).
    - **CRITICAL:** Add `checkin` listener to `DISCARD ALL` to prevent connection pool leakage.

## Acceptance Criteria
- [ ] Database connects successfully.
- [ ] Session context variables are properly scoped (verified in later stories, but scaffolding must exist).

## Verification Plan
**Manual Verification:**
- Run `curl http://localhost:8000/health/deep` (implemented in Epic 1, now connects to real DB).
