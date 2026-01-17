# Epic 1: Walking Skeleton
**User Story:** As a Developer, I want a working local environment with Backend, Frontend, and Database running in containers, so that I can start building features on a solid foundation.

**Goal:** A working "Hello World" system where Backend (FastAPI) and Frontend (React) run locally via Docker/Make, linting passes, and CI is green.

## Traceability Matrix
| Roadmap Step (docs/03) | Story File | Status |
| :--- | :--- | :--- |
| Step 1.1 | `story-01-01-init-repo.md` | Pending |
| Step 1.2 | `story-01-02-backend-bootstrap.md` | Pending |
| Step 1.3 | `story-01-03-fastapi-setup.md` | Pending |
| Step 1.4 | `story-01-04-frontend-bootstrap.md` | Pending |
| Step 1.5 | `story-01-05-docker-compose.md` | Pending |
| Step 1.6 | `story-01-06-quality-tooling.md` | Pending |
| Step 1.7 | `story-01-07-makefile.md` | Pending |
| Step 1.8 | `story-01-08-secrets.md` | Pending |

## Execution Order
1.  [x] `story-01-01-init-repo.md`
2.  [x] `story-01-02-backend-bootstrap.md`
3.  [x] `story-01-03-fastapi-setup.md`
4.  [x] `story-01-04-frontend-bootstrap.md`
5.  [x] `story-01-05-docker-compose.md`
6.  [x] `story-01-06-quality-tooling.md`
7.  [x] `story-01-07-makefile.md`
8.  [x] `story-01-08-secrets.md`

## Epic Verification
**Completion Criteria:**
- [ ] `make install-all` runs without error.
- [ ] `docker compose up` starts API (port 8000), Frontend (port 5173), DB (5432).
- [ ] Accessing `http://localhost:8000/health` returns 200 OK.
- [ ] Accessing `http://localhost:5173` loads the React app.
- [ ] `make check` passes (linting, types, tests).
