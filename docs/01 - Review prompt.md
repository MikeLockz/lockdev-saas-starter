Role: Act as a Senior Staff Software Architect and CTO with 20+ years of experience in high-scale systems Healthcare/HIPAA compliance.

Task: Conduct a critical review of my proposed tech stack for a new project. Identify architectural risks, potential bottlenecks, maintenance overhead, and "silver bullet" fallacies.

Project Context:

Goal: Building a multi-tenant with logical isolation healthcare platform with a patient mobile app and a call-center workflow.

Primary Personas: Patients, Admin staff, Call center agents

Key Constraints: Must be HIPAA compliant, 2-person dev team, needs to launch MVP in 3 months.

Integration Needs: Heavy reliance on 3rd party APIs for telephony and EHR data.

The Proposed Stack:

**Principles:**

* HIPAA Compliant (via BAA inheritance)
* Operationally Boring (AWS and Aptible)
* AI-Native (Python/FastAPI + Bedrock)
* Compatible with AI for development (lots of existing examples and great documentation)
* Easy to understand (minimal layers, abstractions, coupling)
* Cost effective with minimal vendor contracts
* Room to grow and evolve tooling, integrations, vendor solutions when revenue allows

**Infra:**

* **Hosting:** Aptible (Dedicated Stack)
  * SSL certs
* **AWS Integration (via BAA):**
  * Accounts:
    * prod: provisioned with IaC
    * dev: local development to use real services
  * Services:
    * S3 (Storage + Encryption)
    * SES (Transactional Email)
    * Textract / Bedrock (AI features)
    * Route53 (DNS)
    * Secrets Manager
      * GOOGLE_SERVICE_ACCOUNT_JSON=GCP service account with "Firebase Auth Admin"
* **GCP (BAA):**
  * Identiy platform
    * Accept BAA
    * Disable analytics


* **IaC (OpenTofu/Terraform):**
* *Scope:* AWS S3 Buckets, IAM Policies, KMS Keys (Stateful/Risky items only).
* *Strategy:* "Compliance Sandwich" (Aptible manages app resources, Terraform manages data resources).


* **CI/CD:** GitHub Actions
* **Secrets:** SOPS + Age (for local dev), Aptible Env Vars (production)

**Structure:**

* **Monorepo:** `make` (Manage Python + TS together)
  * install (setup local dev environment)
  * dev (start all services)
    * Honcho for process management
  * migrate (database migrations)
    * create (new migration)
    * db-reset (nuke db)
      * including triggers
  * check (pre-ci to catch failing github actions)
    * lint (biome and ruff)
    * format (biome and ruff)
  * test (frontend and backend)
  

**Quality:**

* **TS Lint/Format:** Biome
* **Python Lint:** ruff
* **E2E:** Playwright


**Documentation:** Architecture as Code
* **C4:** Structurizer for L1 and L2
* **D2:** User journey and process mapping
* **OpenAPI:** Generated automatically

**Front End (SPA):**
Light front end that prioritizes simplicity and speed. No authoritative business or client-side processing.

* **Framework:** Vite + React (Drop "TanStack Start" for MVP stability)
* **Routing:** TanStack Router
* **Server State/Data:** TanStack Query
* **Client state:** Zustand
* **UI:** Shadcn/ui
  * Components are designed to be mobile friendly with large hit targets and adequit padding
* **Auth:** GCP Firebase SDK
  * firebase
  * react-firebase-hooks
* **API Client:** Orval or `openapi-typescript-codegen` (Auto-generate from FastAPI `openapi.json`)
* **Mobile:** Capacitor (app wrapper)

**Back End (Container):**
All business logic. Integrations other services and databases.

* **Runtime:** Python 3.11+
* **Framework:** FastAPI
  * **Read access logging:** Write custom logger on routes that return PHI
  * **Server:** `uvicorn` 
* **Package Manager:** `uv`
* **Agentic Framework:** PydanticAI (tool calling, convo history, retries)
* **Validation:** Pydantic v2
  * pydantic-settings (validate config on startup)
* **CRUD Views:** sqladmin (internal super admin)
* **Logging:** `structlog` (JSON logs for machine parsing)
  * single-line in prod
  * mask PHI from logs
* **AI Logging:** `logfire` (debug structured data pipelines)
* **PII Masking:** Presidio (runs async on worker only)
  * scrub user generated content
  * scrub data that will be stored or processed by LLM (ie visit summary)
* **Database ORM:** SQLAlchemy + Alembic
  * asyncio (AsyncSession) with asyncpg driver
    * do not use psycopg2
* **Auth:** * firebase-admin
  * Define auth dependency as a standard def (non-async) to run in thread pool
* **Audit:** `postgresql-audit` (Trigger-based history)
* **Errors:** sentry sdk: global exception handler (Override HTTPException and RequestValidationError)
* **Traces:** sentry sdk: middleware on every inbound request (X-Request-ID header)
  * returns in response Headers
  * injects into structlog
  * injects to db query comments
* **Middleware:** 
  * TrustedHostMiddleware (Security) at the very top
  * CORSMiddleware near the top
  * GZipMiddleware should be near the bottom
  * Tenant Context: extracts the Tenant ID from the request/user and applies a filter to every SQLAlchemy query automatically
* **Healthcheck:**
  * **/health:** Returns 200 OK instantly (shows the web server is up)
  * **/health/deep:** Monitoring endpoint. Checks the Database connection and Redis connection
* **httpx:** set default timeout to 10s on all external calls
  

**Background Worker (Container):**

* **Task Runner:** **ARQ** (Redis-based, async-native, simpler than Celery for FastAPI)
  * idempotent execution
* **Scheduled Jobs:** ARQ integration
  * idempotent execution

**Data Persistence:**

* **Database:** Aptible Managed Postgres 15+ (Encrypted at rest)
  * Row level security
* **Cache:** Aptible Managed Redis
* **Object Storage:** **AWS S3** (Private, SSE-KMS Encrypted)
  * Ensure same region as Aptible
  * Target for aptible log drain

**Security & Compliance:**

* **Policy as Code:** Checkov (Scans Terraform & Dockerfiles)
* **Virus Scanning:** AWS Lambda function (Triggered on S3 Upload)
* **Headers:** Helmet

**Observability:**
* **Logging:** CloudWatch Log Insights
* **Traces:** Sentry ($80/month start)
* **APM:** Sentry
* **Alerting:** Sentry
* **User session analytics:** Sentry


Please evaluate based on:

Developer Velocity: Is this stack too heavy for a small team that is heavily reliant on LLM for writing code?
Extensibility: Is this stack easy to modify with additional integrations and features in a composible and decoupled way?
Performance: Is this going to provide an ideal experience for customers and providers?
Security & Compliance: Are there any glaring holes for a Healthcare/SaaS context?
Alternative Suggestions: If a specific tool is "overkill" or "legacy," suggest a modern, leaner alternative.
Output Format: Provide the review in a structured Markdown format with a "Risk Level" (Low/Medium/High) for each category.
