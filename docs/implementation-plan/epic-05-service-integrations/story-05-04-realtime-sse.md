# Story 5.4: Real-Time Updates (SSE)
**User Story:** As a User, I want to see updates immediately without refreshing, so that I can react quickly.

## Status
- [x] **Complete**

## Context
- **Roadmap Ref:** Step 5.4 from `docs/03`

## Technical Specification
**Goal:** Implement Server-Sent Events.

**Changes Required:**
1.  **File:** `backend/src/api/events.py`
    - `EventGenerator`.
    - `GET /api/events` endpoint.
    - Redis Pub/Sub listener.

## Acceptance Criteria
- [x] Client receives events pushed from backend.

## Verification Plan
**Manual Verification:**
- `curl -N localhost:8000/api/events`. Trigger event. Verify output.
