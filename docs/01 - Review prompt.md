Role: Act as a Senior Staff Software Architect and CTO with 20+ years of experience in high-scale systems Healthcare/HIPAA compliance.

Task: Conduct a critical review of my proposed tech stack for a new project. Identify architectural risks, potential bottlenecks, maintenance overhead, and "silver bullet" fallacies.

Project Context:

Goal: Building a multi-tenant with logical isolation healthcare platform with a patient mobile app and a call-center workflow.

Primary Personas: Patients (Self-Managed & Dependent), Proxies (Guardians/POA), Providers, Clinical Staff, Administrative Staff, Call Center Agents, Organization Admins, Super Admins

Key Constraints: Must be HIPAA compliant, 2-person dev team, needs to launch MVP in 3 months.

Integration Needs: Heavy reliance on 3rd party APIs for telephony and EHR data.

---

## Data Model Requirements

### User Actors & Roles

**Clinical & Operational Staff:**
- **Provider**: Licensed clinician (MD, DO, NP, PA). Holds unique identifiers (NPI, DEA). Can work across multiple Organizations.
- **Clinical Staff**: Support personnel (Nurses, Medical Assistants) assisting Providers with patient data access.
- **Administrative Staff**: Front-desk or billing personnel with scheduling/demographics access, restricted clinical notes.
- **Organization Admin**: Manages settings and user list for a specific Tenant (Organization).

**Patient & Family:**
- **Self-Managed Patient**: Competent adult receiving care with direct login credentials.
- **Dependent Patient**: Minor or incapacitated adult. **No login** - must be accessed via a Proxy.
- **Patient Proxy**: Legal guardian, parent, or power of attorney. Logs in to manage one or more Dependent Patients.

**System & Oversight:**
- **Super Admin**: Platform owner with full access to all tenants for support and maintenance.
- **Auditor/Compliance Officer**: Read-only access to Audit Logs; restricted PHI access.
- **Service Account (Bot)**: Non-human users (e.g., "Billing System Integration") for accurate API logging.

### Functional Requirements

- **FR-01 User/Profile Separation**: System must decouple `User` (login credentials) from `Role` (Patient, Provider). Single email can hold multiple roles (e.g., Patient at Clinic A and Provider at Clinic B).
- **FR-02 Multi-Tenancy**: Users can belong to 0-Many Organizations. Data from Org A must never leak to Org B unless explicitly shared.
- **FR-03 Proxy Management**: Proxy can manage multiple Patients (1-to-Many). Patient can have multiple Proxies (Many-to-Many).
- **FR-04 Granular Consent**: Proxy relationships must support granular scopes: `can_view_clinical`, `can_view_billing`, `can_schedule`.
- **FR-05 Safe Contact Protocol**: System must distinguish standard phone number from "safe" contact method. Logic must prevent automated messages/voicemails to non-safe numbers (e.g., domestic violence situations).

### Core Data Entities

| Entity | Description | Key Attributes |
| --- | --- | --- |
| **Organization** | The tenant (Clinic/Hospital) | `id`, `name`, `tax_id`, `settings_json` |
| **User** | The authentication record | `id`, `email`, `password_hash`, `mfa_enabled` |
| **AuditLog** | Immutable record of actions | `actor_id`, `target_resource`, `action_type`, `ip_address`, `timestamp` |

### Role Entities

| Entity | Description | Key Attributes |
| --- | --- | --- |
| **Provider** | Licensed clinician profile | `npi_number`, `dea_number`, `state_licenses` (Array) |
| **Staff** | Non-provider employee | `employee_id`, `job_title` (e.g., Nurse, Biller) |
| **Patient** | The receiver of care | `mrn` (Medical Record Number), `dob`, `legal_sex`, `gender_identity` |
| **Proxy** | The manager of care | `relationship_type` (Parent, Guardian) |

### Association & Logic Tables

- **Organization_Member**: Links `User` to `Organization` with a specific role (Provider, Staff).
- **Patient_Proxy_Assignment**: Links `Proxy` to `Patient`. Attributes: `permissions_mask` (Binary/JSON for read/write scope), `relationship_proof` (document ID for POA).
- **Care_Team**: Links `Provider` to `Patient` within an `Organization`.

### Contact & Demographics

- **Contact_Method**: `type` (Mobile, Home, Email), `value`, `is_primary`, `is_safe_for_voicemail` (Boolean - **Critical for patient safety**)

### Non-Functional Requirements (Compliance)

- **NFR-01**: Every Read/Write operation on Patient record must generate an `AuditLog` entry.
- **NFR-02**: Audit logs must be immutable and stored for minimum 6 years (HIPAA retention).
- **NFR-03**: All PHI must be encrypted at rest and in transit.
- **NFR-04**: Super Admins cannot view PHI without generating explicit "Break Glass" audit log event.

### Assumptions

1. **US-Centric**: NPI and DEA identifiers are specific to US healthcare system.
2. **Email as Identity**: Email is the unique identifier for `User` accounts.
3. **Soft Deletes**: No clinical data is hard deleted; only soft deleted (`deleted_at` timestamp).

---

The Proposed Stack:

**Principles:**

* HIPAA Compliant (via BAA inheritance)
* Operationally Boring (AWS and Aptible)
* AI-Native (Python/FastAPI + Google Gemini)
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
    * Connect (Call Center & IVR)
    * End User Messaging (SMS)
    * Textract (OCR)
    * Route53 (DNS)
      * app.domain.com (Frontend)
      * api.domain.com (Backend)
    * Secrets Manager
      * GOOGLE_SERVICE_ACCOUNT_JSON=GCP service account with "Identity Platform Admin"
* **GCP (BAA):**
  * Identiy platform
    * Accept BAA
    * Disable analytics
  * **Vertex AI:**
    * Google Gemini


* **IaC (OpenTofu/Terraform):**
* *Scope:* AWS S3 Buckets, IAM Policies, KMS Keys (Stateful/Risky items only).
* *Strategy:* "Compliance Sandwich" (Aptible manages app resources, Terraform manages data resources).


* **CI/CD:** GitHub Actions
* **Secrets:** SOPS + Age (local keys.txt), Aptible Env Vars (production)

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
* **Enforcement:** pre-commit
* **E2E:** Playwright


**Documentation:** Architecture as Code
* **C4:** Structurizer for L1 and L2
* **D2:** User journey and process mapping
* **OpenAPI:** Generated automatically

**Front End (SPA):**
Light front end that prioritizes simplicity and speed. No authoritative business or client-side processing.

* **Framework:** Vite + React (Drop "TanStack Start" for MVP stability)
* **Routing:** TanStack Router
* **Server State/Data:** TanStack Query (online only)
* **Client state:** Zustand
* **UI:** Shadcn/ui
  * Components are designed to be mobile friendly with large hit targets and adequit padding
* **Forms:** React Hook Form + Zod
* **Auth:** Google Cloud Identity Platform (GCIP)
  * firebase (client sdk works with GCIP)
  * react-firebase-hooks
* **API Client:** Orval or `openapi-typescript-codegen` (Static generation via `generate_schema.py` -> TS Types + Zod Schemas)
* **Mobile:** Capacitor (app wrapper) + vite-plugin-pwa (Online Only - No PHI Cache)

**Back End (Container):**
All business logic. Integrations other services and databases.

* **Runtime:** Python 3.11+
* **Framework:** FastAPI
  * **Read access logging:** Audit Middleware (Logs 'READ' events on `/api/staff/*`)
  * **Server:** `uvicorn` 
* **Package Manager:** `uv`
* **Agentic Framework:** Vertex AI SDK + Pydantic (No agentic framework abstraction)
* **Validation:** Pydantic v2
  * pydantic-settings (validate config on startup)
* **CRUD Views:** sqladmin (internal super admin)
* **Logging:** `structlog` (JSON logs for machine parsing)
  * single-line in prod
  * mask PHI from logs (Key-based masking only)
* **Rate Limiting:** `slowapi` (Redis-backed in Prod)
* **AI Logging:** `structlog` (JSON)
* **PII Masking:** Presidio (Exceptions only)
  * scrub user generated content
  * scrub data that will be stored or processed by LLM (ie visit summary)
* **Database ORM:** SQLAlchemy + Alembic
  * asyncio (AsyncSession) with asyncpg driver
    * do not use psycopg2
* **Auth:** * Google Cloud Identity Platform (via firebase-admin)
  - define auth dependency as a standard def (non-async) to run in thread pool
  - **MFA:** Enforce MFA for all Internal Staff (Clinician/Admin)
* **Audit:** `postgresql-audit` (Trigger-based history)
* **Data Integrity:** ULID for all Primary Keys (Lexicographically Sortable)
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
  * Row Level Security (RLS) for Tenant Isolation
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
