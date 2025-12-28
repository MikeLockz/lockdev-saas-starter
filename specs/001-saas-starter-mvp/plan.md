# Implementation Plan: Initial SaaS Starter MVP Platform

**Branch**: `001-saas-starter-mvp` | **Date**: 2025-12-27 | **Spec**: [specs/001-saas-starter-mvp/spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-saas-starter-mvp/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan outlines the implementation of the Initial SaaS Starter MVP, a HIPAA-compliant multi-tenant healthcare platform. It includes core tenant management, patient registration via a mobile-friendly web app, call center workflows, AI-assisted document extraction, simple subscription billing, and integration with Healthie EHR. The architecture prioritizes operational simplicity and security, utilizing a Python/FastAPI backend, React frontend, and managed infrastructure (Aptible/AWS).

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.0+ (Frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic, React, TanStack Query/Router, Shadcn/ui
**Storage**: PostgreSQL (Data), Redis (Cache/Workers), AWS S3 (Documents)
**Testing**: Pytest (Backend), Vitest (Frontend), Playwright (E2E)
**Target Platform**: Docker Containers (Aptible), AWS Lambda (optional for specific tasks), Web Browsers
**Project Type**: Monorepo (Web Application + API + Workers)
**Performance Goals**: <1s API response for search, <30s AI extraction
**Constraints**: HIPAA Compliance (Encryption, Audit, Masking), Multi-tenancy isolation
**Scale/Scope**: Initial MVP, support for 50 concurrent agents

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **HIPAA Compliance**: Does this feature handle PHI? If so, are encryption, audit, and access controls defined? (Yes, explicitly required in Spec SEC-001, SEC-002, SEC-003)
- [x] **Operational Simplicity**: Does this introduce new infrastructure? If so, is it managed/boring? (Yes, leveraging defined stack: Aptible, AWS, Standard Python/TS libs)
- [x] **AI-Native**: Is the implementation compatible with AI-assisted development (clear patterns, typed interfaces)? (Yes, Python/Pydantic/TS enforce types)
- [x] **Simplicity**: Are abstractions minimal and necessary? (Yes, standard SPA + API + Worker architecture)

## Project Structure

### Documentation (this feature)

```text
specs/001-saas-starter-mvp/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/             # FastAPI routers
│   ├── core/            # Config, security, database setup
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic schemas (Requests/Responses)
│   ├── services/        # Business logic (Auth, Tenant, Patient, Subscription)
│   ├── workers/         # ARQ worker tasks (AI extraction, Healthie sync)
│   └── integrations/    # External clients (Healthie, Bedrock, S3)
└── tests/
    ├── unit/
    └── integration/

frontend/
├── src/
│   ├── components/      # Shared UI components (Shadcn)
│   ├── features/        # Feature-based modules (Auth, Patient, Agent)
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utilities (API client, formatting)
│   └── routes/          # TanStack Router definitions
└── tests/
```

**Structure Decision**: Standard Web Application Monorepo structure separating Frontend and Backend, with clear modularization by feature/domain.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | | |