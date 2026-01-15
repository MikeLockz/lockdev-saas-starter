# Story 6.1: C4 Model (Structurizr)
**User Story:** As an Architect, I want C4 diagrams, so that I can communicate system boundaries and containers.

## Status
- [x] **Complete**

## Context
- **Roadmap Ref:** Step 6.1 from `docs/03`

## Technical Specification
**Goal:** Create `docs/architecture/workspace.dsl`.

**Changes Required:**
1.  **File:** `docs/architecture/workspace.dsl`
    - Define Person (Patient, Staff, Call Agent, Super Admin).
    - Define System (Lockdev, Firebase, Stripe, AWS, Vertex AI, Sentry).
    - Define Containers (API, SPA, Worker, DB, Redis).
    - Define Components (Auth, Consent, User, Billing, Documents modules).
    - Add Dynamic View for Patient Registration flow.

## Acceptance Criteria
- [x] DSL exports to PlantUML/JSON without error.

## Verification Plan
**Manual Verification:**
- Run `structurizr-cli export ...`.
