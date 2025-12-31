# Story 1.5: Containerization (Docker Compose)
**User Story:** As a Developer, I want to run the full stack with a single command, so that my local environment matches production components.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 1.5 from `docs/03`

## Technical Specification
**Goal:** Create `docker-compose.yml` to orchestrate services.

**Changes Required:**
1.  **File:** `docker-compose.yml`
    - **Service: db:** Postgres 15 (`app_db`, user `app`).
    - **Service: redis:** Redis 7.
    - **Service: api:** Build `./backend`, command `uvicorn`, ports `8000:8000`, depends_on `db`.
    - **Service: web:** Build `./frontend`, command `pnpm dev`, ports `5173:5173`.
    - **Volumes:** Mount code directories for hot-reloading.

## Acceptance Criteria
- [ ] `docker compose up --build` starts all services.
- [ ] API can talk to DB (connectivity check).

## Verification Plan
**Manual Verification:**
- Command: `docker compose up`
- Check: `docker compose ps` shows all healthy/running.
