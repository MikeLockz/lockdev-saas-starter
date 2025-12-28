# Quickstart: Initial SaaS Starter MVP Platform

## Prerequisites

-   Docker & Docker Compose
-   Python 3.11+
-   Node.js 20+
-   AWS Credentials (for Bedrock/S3 dev)

## Setup

1.  **Clone & Install**:
    ```bash
    git clone <repo>
    cd <repo>
    make install
    ```

2.  **Environment**:
    Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    # Populate AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY for local Bedrock
    # Populate HEALTHIE_API_KEY for Healthie Dev Sandbox
    ```

3.  **Run Services**:
    ```bash
    make dev
    ```
    This starts:
    -   PostgreSQL (Port 5432)
    -   Redis (Port 6379)
    -   Backend API (Port 8000)
    -   Frontend (Port 3000)
    -   Worker (ARQ)

## Verification

1.  **Backend Health**:
    Visit `http://localhost:8000/health` -> Should return `{"status": "ok"}`

2.  **API Docs**:
    Visit `http://localhost:8000/docs` -> Swagger UI

3.  **Frontend**:
    Visit `http://localhost:3000` -> Login Screen

## Common Tasks

-   **Create Tenant**:
    ```bash
    docker compose exec backend python scripts/create_tenant.py --name "Demo Clinic"
    ```

-   **Run Tests**:
    ```bash
    make test
    ```
