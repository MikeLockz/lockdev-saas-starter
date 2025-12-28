---
description: "Task list for Initial SaaS Starter MVP Platform"
---

# Tasks: Initial SaaS Starter MVP Platform

**Input**: Design documents from `/specs/001-saas-starter-mvp/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create monorepo structure (backend/, frontend/, workers/) in project root
- [ ] T002 Initialize Python 3.11+ backend with FastAPI and UV in backend/
- [ ] T003 [P] Initialize React+Vite frontend with TypeScript and Shadcn/ui in frontend/
- [ ] T004 [P] Configure Docker Compose for Postgres, Redis, Backend, Frontend in docker-compose.yml
- [ ] T005 [P] Setup pre-commit hooks (Biome, Ruff) in .pre-commit-config.yaml
- [ ] T006 [P] Configure CI/CD pipeline for tests and linting in .github/workflows/ci.yml

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Setup SQLAlchemy with asyncpg and Alembic migrations in backend/src/core/db.py
- [ ] T008 [P] Implement structured logging with Structlog (masking PHI) in backend/src/core/logging.py
- [ ] T009 [P] Implement global error handling and custom exceptions in backend/src/core/exceptions.py
- [ ] T010 [P] Configure environment variables (Pydantic Settings) in backend/src/core/config.py
- [ ] T011 Create base SQLAlchemy model with UUID and AuditMixin in backend/src/models/base.py
- [ ] T012 Implement Row-Level Security (RLS) helpers/middleware in backend/src/core/security.py
- [ ] T013 Setup ARQ worker configuration in backend/src/core/worker.py
- [ ] T014 [P] Setup frontend API client (TanStack Query + Axios) in frontend/src/lib/api.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

## Phase 3: User Story 1 - Tenant & Admin Setup (Priority: P1) 🎯 MVP

**Goal**: Provision isolated tenants and manage staff accounts securely.

**Independent Test**: Create a tenant via CLI/API, create an admin user, and verify login/token.

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create Tenant model in backend/src/models/tenant.py
- [ ] T016 [P] [US1] Create User model in backend/src/models/user.py
- [ ] T017 [P] [US1] Create AuditLog model in backend/src/models/audit.py
- [ ] T018 [US1] Implement TenantService (create, get) in backend/src/services/tenant.py
- [ ] T019 [US1] Implement UserService (create_admin, authenticate) in backend/src/services/user.py
- [ ] T020 [US1] Implement Auth router (login, refresh) in backend/src/api/auth.py
- [ ] T021 [US1] Implement SuperAdmin router (manage tenants) in backend/src/api/admin.py
- [ ] T022 [P] [US1] Implement Login page in frontend/src/features/auth/LoginPage.tsx
- [ ] T023 [P] [US1] Implement Admin Dashboard layout in frontend/src/features/admin/AdminLayout.tsx
- [ ] T024 [US1] Verify PHI masking in logs/traces (Compliance)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

## Phase 4: User Story 2 - Patient Registration & Mobile App (Priority: P1)

**Goal**: Patient registration, profile management, and Healthie sync.

**Independent Test**: Register as patient, log in, view dashboard, verify Healthie push.

### Implementation for User Story 2

- [ ] T025 [P] [US2] Create Patient model in backend/src/models/patient.py
- [ ] T026 [P] [US2] Create Subscription/Payment models in backend/src/models/billing.py
- [ ] T027 [US2] Implement HealthieClient (create_patient) in backend/src/integrations/healthie.py
- [ ] T028 [US2] Implement PatientService (CRUD + Healthie Sync) in backend/src/services/patient.py
- [ ] T029 [US2] Implement Patient router (register, profile) in backend/src/api/patient.py
- [ ] T030 [US2] Implement SubscriptionService (create_subscription, process_payment) in backend/src/services/subscription.py
- [ ] T031 [US2] Implement Billing router (subscribe, webhook) in backend/src/api/billing.py
- [ ] T032 [P] [US2] Implement Patient Registration form in frontend/src/features/patient/RegisterPage.tsx
- [ ] T033 [P] [US2] Implement Subscription/Billing UI component in frontend/src/features/patient/Billing.tsx
- [ ] T034 [P] [US2] Implement Patient Dashboard in frontend/src/features/patient/DashboardPage.tsx
- [ ] T035 [US2] Configure Localization (i18n) for English/Spanish in frontend/src/lib/i18n.ts

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

## Phase 5: User Story 3 - Call Center Workflow (Priority: P2)

**Goal**: Agents search/view patients and audit access.

**Independent Test**: Login as Agent, search patient, verify audit log entry.

### Implementation for User Story 3

- [ ] T036 [US3] Implement AgentService (search_patients) in backend/src/services/agent.py
- [ ] T037 [US3] Implement Agent router (search, get_patient) in backend/src/api/agent.py
- [ ] T038 [P] [US3] Implement Patient Search component in frontend/src/features/agent/PatientSearch.tsx
- [ ] T039 [P] [US3] Implement Patient Detail view for Agents in frontend/src/features/agent/PatientDetail.tsx
- [ ] T040 [US3] Verify AuditLog entries created on search/view actions

**Checkpoint**: All user stories should now be independently functional

## Phase 6: User Story 4 - AI-Assisted Document Extraction (Priority: P3)

**Goal**: Upload PDF, extract data via AI, update patient record.

**Independent Test**: Upload PDF, wait for job, verify extracted data.

### Implementation for User Story 4

- [ ] T041 [P] [US4] Create Document model in backend/src/models/document.py
- [ ] T042 [US4] Implement S3Client (upload, presign) in backend/src/integrations/s3.py
- [ ] T043 [US4] Implement BedrockClient (extract_data) in backend/src/integrations/bedrock.py
- [ ] T044 [US4] Implement ARQ worker task for extraction in backend/src/workers/extraction.py
- [ ] T045 [US4] Implement Document router (upload, status) in backend/src/api/document.py
- [ ] T046 [P] [US4] Implement Document Upload component in frontend/src/features/document/Upload.tsx

**Checkpoint**: Full MVP feature set complete.

## Phase 7: Real-time Chat (US5 - Derived)

**Goal**: Secure chat between Patient and Agent.

**Independent Test**: Send message from Patient, receive as Agent, verify DB persistence.

- [ ] T047 [P] [US5] Create Message model in backend/src/models/message.py
- [ ] T048 [US5] Implement WebSocket endpoint for Chat in backend/src/api/chat.py
- [ ] T049 [P] [US5] Implement Chat UI component in frontend/src/features/chat/ChatWindow.tsx

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T050 [P] Update API documentation (OpenAPI)
- [ ] T051 Run security scan (Checkov/Bandit)
- [ ] T052 Performance tune database indexes
- [ ] T053 Final validation of HIPAA compliance (Audit, Encryption)

## Dependencies & Execution Order

- **Setup & Foundational**: Blocks everything.
- **US1 (Tenant/Admin)**: Blocks US2, US3, US4.
- **US2 (Patient)**: Independent of US3/US4.
- **US3 (Agent)**: Depends on US2 (needs patients).
- **US4 (AI)**: Depends on US2 (needs patients).
- **US5 (Chat)**: Depends on US2 and US3.

## Implementation Strategy

1.  **MVP Core**: Setup -> Foundational -> US1 -> US2. This enables Patient onboarding.
2.  **Workflow**: Add US3 for Call Center.
3.  **Differentiation**: Add US4 (AI) and US5 (Chat) to complete the MVP.
