# LockDev SaaS Starter

## Repository Structure

This repository follows a specific structure where the `main` branch is reserved for **Documentation, Specifications, and Agentic Tools**, while the actual application implementation resides in separate branches.

### Branches

- **`main`**: The Source of Truth for *Requirements*.
    - Contains `docs/` (Specifications, Implementation Plans, Architectural decisions).
    - Contains `contracts/` (Data schemas, API definitions, JSON specs).
    - Contains `agent/` (The "Genesis" System Architect and other agentic tools).
    - **NO** application code (Frontend/Backend) exists here.

- **`impl/initial-bootstrap`**: The baseline implementation.
    - Contains the full source code (`apps/`, `infra/`, `docker-compose.yml`).
    - This is the snapshot of the code as of the restructuring.

- **`feat/*`**: Feature branches for ongoing work.

## Workflow

1.  **Plan**: Update specs and plans in `main`.
2.  **Branch**: Create a feature branch or use an implementation branch (e.g., `impl/v1`) based on the specs.
3.  **Execute**: Agents or Developers implement the code in the implementation branch.
4.  **Verify**: Tests run against the implementation branch.

## Directory Layout (Main Branch)

- `agent/`: The Agentic System (Genesis, Polling, etc.).
- `contracts/`: JSON Schemas defining the data model and API.
- `docs/`: Markdown documentation and detailed plans.
- `scripts/`: various utility scripts.
