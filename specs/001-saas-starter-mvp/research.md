# Research: Initial SaaS Starter MVP Platform

**Feature**: `001-saas-starter-mvp`
**Status**: Complete

## Decision 1: Healthie Integration Pattern

**Context**: Requirement for one-way push of Patient demographics from App to Healthie.
**Decision**: Use Healthie GraphQL API.
**Rationale**: Healthie provides a robust GraphQL API which allows for precise data creation and updates. We will map our internal Patient entity to Healthie's Patient input schema.
**Implementation**:
-   Create an `integrations/healthie` module.
-   Implement `create_patient` and `update_patient` functions.
-   Store `healthie_id` on the local Patient record to manage updates.
-   Handle sync failures via background worker retries (ARQ).

## Decision 2: AI Document Extraction

**Context**: Extract medical data from uploaded PDFs (FR-006, SC-005).
**Decision**: AWS Textract + Bedrock (LLM).
**Rationale**:
-   **Textract**: specialized for extracting text and form data from documents (OCR).
-   **Bedrock (Claude 3 Sonnet)**: Excellent reasoning capabilities to structure the raw OCR text into the target JSON schema (Patient Medical History).
-   **Cost/Compliance**: Both are HIPAA eligible and pay-per-use.
**Alternatives Considered**:
-   *Local OCR (Tesseract)*: Lower quality, high operational overhead.
-   *OpenAI API*: Requires external BAA, potential data privacy concerns if not configured correctly (AWS is already in BAA scope).

## Decision 3: Audit Logging Strategy

**Context**: Strict HIPAA requirement to log all PHI access (SEC-003).
**Decision**: Middleware + `postgresql-audit` (Trigger-based).
**Rationale**:
-   **Middleware**: Captures "Who" (User/Tenant) and "When" from the HTTP request context.
-   **Trigger-based (DB)**: Captures "What" (Data changes) reliably, even if app logic bypasses service layer.
-   **Composite**: The middleware injects context (User ID, Request ID) into the DB session (e.g., via local variables or comments), which the trigger captures alongside the data change.
**Alternatives Considered**:
-   *App-level logging only*: Misses direct DB changes, harder to guarantee completeness.

## Decision 4: Multi-Tenancy Implementation

**Context**: Logical isolation of data by Tenant ID (FR-001).
**Decision**: Row-Level Security (RLS) with SQLAlchemy Event Hooks.
**Rationale**:
-   **RLS**: Enforces isolation at the database engine level, preventing accidental leakage even if app filters are missed.
-   **SQLAlchemy**: Use `before_cursor_execute` event to set the current `tenant_id` session variable.
**Alternatives Considered**:
-   *Schema-per-tenant*: Too complex for MVP management (migrations are painful).
-   *App-level filters only*: High risk of developer error leaking data.

## Decision 5: Subscription Management

**Context**: Patient-level subscriptions, simple billing (FR-007).
**Decision**: Stripe Integration (Customer per Patient/Tenant).
**Rationale**:
-   Industry standard for SaaS billing.
-   Simplifies PCI compliance (we don't touch card data).
-   We track `subscription_status`, `current_period_end` locally, but rely on Stripe webhooks for state changes.
