<!-- 
Sync Impact Report:
- Version: 0.0.0 -> 1.0.0 (Initial Ratification)
- Added Principles: HIPAA Compliance, Operational Simplicity, AI-Native Compatibility, Radical Simplicity, Documentation as Code
- Templates Updated: 
  - .specify/templates/spec-template.md (Added Security & Compliance section)
  - .specify/templates/plan-template.md (Added specific Constitution Gates)
-->

# Lockdev SaaS Starter Constitution

## Core Principles

### I. HIPAA Compliance (Non-Negotiable)
**Rule**: All architecture and features MUST support HIPAA compliance requirements.
**Rationale**: The system handles PHI. We inherit compliance via BAA from Aptible/AWS, but application logic must enforce:
1.  **Encryption**: All data at rest and in transit must be encrypted.
2.  **Audit**: All access to PHI must be logged (who, what, when).
3.  **Access Control**: Least privilege access; no PHI in logs/traces (masking required).

### II. Operational Simplicity ("Boring Ops")
**Rule**: Choose managed, proven infrastructure over novel self-hosted solutions.
**Rationale**: We are a small team. We prioritize developer velocity and stability over optimizing infrastructure costs or using "hype" tech.
-   **Hosting**: Aptible (Dedicated Stack) for app, AWS for data/AI.
-   **Secrets**: SOPS/Age for local, Managed Env Vars for prod.
-   **CI/CD**: GitHub Actions.

### III. AI-Native & Compatible
**Rule**: The stack must be optimized for both *using* AI (features) and *being built by* AI (development).
**Rationale**:
-   **Development**: Code patterns must be consistent, typed (Python/TS), and well-documented to allow LLMs to write high-quality code.
-   **Features**: Python/FastAPI backend provides first-class support for AI/ML libraries (Bedrock, LangChain, PydanticAI).

### IV. Radical Simplicity
**Rule**: Minimal layers, minimal abstractions, minimal coupling.
**Rationale**: "One way to do things." Avoid over-engineering.
-   **Monorepo**: Manage everything together.
-   **Frontend**: Vite + React (SPA), no complex SSR unless critical for SEO.
-   **Backend**: FastAPI + SQLAlchemy. Direct and explicit.

### V. Documentation as Code
**Rule**: Architecture and processes must be documented in the repository, not external wikis.
**Rationale**: Ensures documentation stays in sync with code and is accessible to AI agents.
-   **Structurizr**: For C4 diagrams.
-   **OpenAPI**: Source of truth for API contracts.
-   **ADRs**: Record architectural decisions.

## Governance

**Amendment Process**:
1.  Propose changes via Pull Request to this file.
2.  Update `Sync Impact Report` header.
3.  Update version number.
4.  Verify all templates (`.specify/templates/*`) are aligned with new principles.

**Compliance Review**:
-   All Feature Specs MUST include a "Security & Compliance" section.
-   All Implementation Plans MUST pass the "Constitution Check" gates.
-   Code Reviews MUST verify strict adherence to PHI handling rules.

**Version**: 1.0.0 | **Ratified**: 2025-12-27 | **Last Amended**: 2025-12-27