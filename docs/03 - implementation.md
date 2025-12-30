# Implementation Plan - Lockdev SaaS Starter

This plan transforms the technical requirements into a linear, production-grade roadmap. It prioritizes a "Walking Skeleton" approach, ensuring the end-to-end infrastructure is verifiable before adding complex domain logic.

## Analysis & Decisions
*   **Monorepo Strategy:** We will use a root-level `Makefile` to orchestrate `uv` (backend) and `pnpm` (frontend). This avoids the complexity of Nx/Turbo for this specific stack while meeting the "simple" requirement.
*   **LLM Provider:** Google Gemini (Vertex AI) is selected as the primary LLM, with fallback support patterns in place.
*   **Database:** PostgreSQL 15+ with `SQLAlchemy` (Async) and `Alembic` for migrations. `postgresql-audit` will be used for compliance logging.
*   **Identity & Access:** Strict separation of duties. `User` model will differentiate between `PATIENT` (External) and `STAFF` (Internal) via `UserType`. For call-center scenarios, **CALL_CENTER_AGENT** is a sub-type of STAFF with limited permissions. **MFA is mandatory** for all Staff access (including agents).
*   **Data Integrity:** **ULID** is required for ALL primary keys to allow for lexicographical sorting while preventing ID enumeration.
*   **Auth:** Firebase Auth (Client SDK) + Firebase Admin (Backend verification).
*   **Infra:** "Compliance Sandwich" — Aptible (Container Hosting, managed manually via CLI/Dashboard) + AWS (Stateful Services: S3, SES, Route53, managed via OpenTofu). Aptible is intentionally excluded from OpenTofu scope due to limited provider support.
*   **Formatting:** **Biome** replaces Prettier for unified TS/JS/JSON formatting with zero-config. Prettier is not used.
*   **Forms:** **React Hook Form + Zod** is chosen over TanStack Form for wider ecosystem support and existing patterns. TanStack Query and Router are still used.
*   **Client State:** **Zustand** for lightweight client-side state (auth flags, UI preferences). TanStack Query handles all server state.
*   **Observability:** **Sentry** for exception tracking, APM, distributed tracing, and user session analytics (~$80/month). **CloudWatch** for log aggregation.


---

## Phase 1: The Walking Skeleton (Local Dev & CI)
**Goal:** A working "Hello World" system where Backend and Frontend run locally via Docker/Make, linting passes, and CI is green.

### Step 1.1: Initialize Monorepo Structure
*   **File/Path:** `.` (Root)
*   **Action:** Config
*   **Instruction:** Initialize git, create the folder structure, and add a `.gitignore`.
*   **Code/Config Snippet:**
    ```bash
    git init
    mkdir -p backend/src backend/tests frontend/src .github/workflows infra
    touch Makefile
    ```
    *(Add standard python, node, and macos patterns to .gitignore)*
*   **Verification:** `ls -R` shows the structure.

### Step 1.2: Backend Bootstrap (FastAPI + UV)
*   **File/Path:** `backend/pyproject.toml`
*   **Action:** Create
*   **Instruction:** Initialize the Python project using `uv`. Define dependencies: `fastapi`, `uvicorn`, `structlog`, `presidio-analyzer`.
*   **Code/Config Snippet:**
    ```toml
    [project]
    name = "lockdev-api"
    version = "0.1.0"
    requires-python = ">=3.11"
    dependencies = ["fastapi", "uvicorn[standard]", "structlog", "presidio-analyzer", "google-cloud-aiplatform", "arq", "asyncpg", "python-ulid", "slowapi", "httpx", "sentry-sdk[fastapi]", "secure", "honcho"]
    ```
*   **Verification:** `cd backend && uv sync && uv run python -c "import fastapi; print(fastapi.__version__)"`

### Step 1.3: FastAPI App with Middleware Stack
*   **File/Path:** `backend/src/main.py`
*   **Action:** Create
*   **Instruction:** Create the production-ready app shell with the full middleware stack and both health endpoints.
*   **Code/Config Snippet:**
    ```python
    from fastapi import FastAPI
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import Response
    import structlog
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    import secure
    import uuid

    from src.config import settings

    # =============================================================================
    # SENTRY SDK INITIALIZATION
    # =============================================================================
    # Provides: Exception tracking, APM, Distributed Tracing, User Session Analytics
    # Cost: ~$80/month starter tier
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,  # 10% of transactions
        profiles_sample_rate=0.1,  # 10% of profiled transactions
        send_default_pii=False,  # HIPAA: Never send PII to Sentry
    )

    logger = structlog.get_logger()
    
    # Rate Limiting
    limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
    app = FastAPI(title="Lockdev API")
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # =============================================================================
    # SECURITY HEADERS (Helmet equivalent for Python)
    # =============================================================================
    secure_headers = secure.Secure(
        hsts=secure.StrictTransportSecurity().max_age(31536000).include_subdomains(),
        xfo=secure.XFrameOptions().deny(),
        xxp=secure.XXSSProtection().set("1; mode=block"),
        content=secure.ContentTypeOptions().nosniff(),
        referrer=secure.ReferrerPolicy().no_referrer(),
        cache=secure.CacheControl().no_store().must_revalidate(),
    )
    
    # =============================================================================
    # MIDDLEWARE STACK (Order Matters!)
    # =============================================================================
    # 1. TrustedHostMiddleware - Security: Reject requests with spoofed Host headers
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.ALLOWED_HOSTS  # ["api.domain.com", "localhost"]
    )
    
    # 2. CORSMiddleware - Allow cross-origin requests from frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 3. Security Headers Middleware (Helmet equivalent)
    class SecurityHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            response = await call_next(request)
            secure_headers.framework.fastapi(response)
            return response
    
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 4. Request ID Middleware - Injects X-Request-ID for distributed tracing
    class RequestIDMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
            # Bind to structlog context (injected into all logs)
            structlog.contextvars.bind_contextvars(request_id=request_id)
            # Set Sentry transaction tag
            sentry_sdk.set_tag("request_id", request_id)
            response = await call_next(request)
            # Return in response headers
            response.headers["X-Request-ID"] = request_id
            return response
    
    app.add_middleware(RequestIDMiddleware)
    
    # 5. SlowAPI Rate Limiting
    app.add_middleware(SlowAPIMiddleware)
    
    # 6. GZipMiddleware - Compression (near bottom, compresses final response)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # =============================================================================
    # HEALTH ENDPOINTS
    # =============================================================================
    @app.get("/health")
    async def health():
        """Shallow health check - web server is up (instant 200)."""
        return {"status": "ok"}
    
    @app.get("/health/deep")
    async def health_deep():
        """Deep health check - verifies DB and Redis connectivity (monitoring)."""
        from src.database import engine
        from src.cache import redis_client
        from sqlalchemy import text
        
        errors = []
        
        # Check Postgres
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception as e:
            errors.append(f"database: {str(e)}")
        
        # Check Redis
        try:
            await redis_client.ping()
        except Exception as e:
            errors.append(f"redis: {str(e)}")
        
        if errors:
            return {"status": "unhealthy", "errors": errors}
        return {"status": "healthy", "database": "ok", "redis": "ok"}
    
    # Step 4.1 Logging logic is injected via structlog configuration.
    ```
*   **Verification:** `cd backend && uv run uvicorn src.main:app --reload` -> visit `/health` (200) and `/health/deep` (checks DB/Redis)

### Step 1.4: Frontend Bootstrap (Vite + React + TS)
*   **File/Path:** `frontend/package.json`
*   **Action:** Create
*   **Instruction:** Initialize Vite React TS project using pnpm. Install core dependencies including Zustand for client state.
*   **Code/Config Snippet:**
    ```bash
    cd frontend
    pnpm create vite . --template react-ts
    pnpm install
    pnpm add zustand @tanstack/react-query @tanstack/react-router axios
    ```
*   **File/Path:** `frontend/src/lib/axios.ts`
*   **Action:** Create
*   **Instruction:** Configure Axios with **domain whitelisting** to prevent requests to unauthorized endpoints.
    ```typescript
    import axios from 'axios';
    
    // SECURITY: Domain whitelist for all outbound HTTP requests
    const ALLOWED_DOMAINS = [
      'api.lockdev.com',
      'localhost:8000',
      'identitytoolkit.googleapis.com',  // Firebase Auth
      'securetoken.googleapis.com',       // Firebase Token refresh
    ];
    
    const apiClient = axios.create({
      baseURL: import.meta.env.VITE_API_URL,
      timeout: 10000,
      withCredentials: true,
    });
    
    // Intercept ALL requests and validate domain
    apiClient.interceptors.request.use((config) => {
      const url = new URL(config.url!, config.baseURL);
      const isAllowed = ALLOWED_DOMAINS.some(
        (domain) => url.host === domain || url.host.endsWith(`.${domain}`)
      );
      
      if (!isAllowed) {
        console.error(`Blocked request to unauthorized domain: ${url.host}`);
        return Promise.reject(new Error(`Domain not whitelisted: ${url.host}`));
      }
      
      return config;
    });
    
    export default apiClient;
    ```
*   **UI Design Constraint:** All components must be **mobile-friendly** with large hit targets (min 44x44px) and adequate padding for touch interfaces.
*   **Verification:** `cd frontend && pnpm dev` -> visit `http://localhost:5173`. Attempt request to non-whitelisted domain -> blocked.

### Step 1.5: Containerization (Docker Compose)
*   **File/Path:** `docker-compose.yml`
*   **Action:** Create
*   **Instruction:** Define services for `api` (using uv), `web` (vite), and `db` (postgres). Mount volumes for hot-reloading.
*   **Code/Config Snippet:**
    ```yaml
    services:
      db:
        image: postgres:15
        environment:
          POSTGRES_USER: app
          POSTGRES_DB: app_db
          POSTGRES_PASSWORD: dev
        ports: ["5432:5432"]
      api:
        build: ./backend
        command: uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
        volumes: ["./backend:/app"]
        depends_on: [db]
        ports: ["8000:8000"]
      web:
        build: ./frontend
        command: pnpm dev --host
        volumes: ["./frontend:/app"]
        ports: ["5173:5173"]
    ```
*   **Verification:** `docker compose up --build`. Access both localhost:8000/health and localhost:5173.

### Step 1.6: Quality Tooling & Enforcement
*   **File/Path:** `.pre-commit-config.yaml` (Root)
*   **Action:** Create
*   **Instruction:** Create `.pre-commit-config.yaml` to run `ruff` and `biome` on staged files. Biome replaces Prettier for unified linting/formatting.
*   **Code/Config Snippet:**
    ```yaml
    repos:
      - repo: https://github.com/astral-sh/ruff-pre-commit
        rev: v0.4.4
        hooks:
          - id: ruff
            args: [ --fix ]
          - id: ruff-format
      - repo: local
        hooks:
          - id: biome-check
            name: biome check
            entry: pnpm biome check
            language: system
            types: [ text ]
            files: \.(ts|tsx|js|jsx|json|css)$
    ```
*   **File/Path:** `biome.json` (Root)
*   **Action:** Create
*   **Instruction:** Configure Biome for unified linting/formatting of TS/JS/JSON (replaces Prettier).
*   **Verification:** `pnpm biome check .`
*   **File/Path:** `backend/pyproject.toml`
*   **Action:** Update
*   **Instruction:** Add `ruff` configuration for Python linting.
*   **Verification:** 
    *   `pre-commit run --all-files`
    *   **Typecheck (Frontend):** `cd frontend && pnpm tsc --noEmit`
    *   **Typecheck (Backend):** `cd backend && uv run mypy src/ --ignore-missing-imports`

### Step 1.7: The Makefile
*   **File/Path:** `Makefile`
*   **Action:** Create
*   **Instruction:** Abstract common commands including dev, db operations, quality checks, and tests.
*   **Code/Config Snippet:**
    ```makefile
    # Better Makefile pattern
    .PHONY: install-all
    install-all:
    	@echo "Installing Backend (includes honcho for process management)..."
    	cd backend && uv sync
    	@echo "Installing Frontend..."
    	cd frontend && pnpm install

    .PHONY: dev
    dev:
    	# honcho is installed as a dev dependency via uv sync
    	cd backend && uv run honcho start -f ../Procfile.dev

    dev-backend:
    	cd backend && uv run uvicorn src.main:app --reload

    dev-frontend:
    	cd frontend && pnpm dev

    # Database commands
    .PHONY: migrate migrate-create db-reset
    migrate:
    	cd backend && uv run alembic upgrade head

    migrate-create:
    	cd backend && uv run alembic revision --autogenerate -m "$(name)"

    db-reset:
    	@echo "⚠️  Nuking database (including triggers)..."
    	cd backend && uv run alembic downgrade base
    	cd backend && uv run alembic upgrade head

    # Quality checks (pre-CI)
    .PHONY: check lint format typecheck
    check: lint typecheck test

    lint:
    	cd backend && uv run ruff check . --fix
    	cd frontend && pnpm biome check --apply .

    format:
    	cd backend && uv run ruff format .
    	cd frontend && pnpm biome format --write .

    typecheck:
    	cd backend && uv run mypy src/ --ignore-missing-imports
    	cd frontend && pnpm tsc --noEmit

    # Tests
    .PHONY: test test-backend test-frontend
    test: test-backend test-frontend

    test-backend:
    	cd backend && uv run pytest tests/ -v

    test-frontend:
    	cd frontend && pnpm vitest run
    ```
*   **Verification:** `make install-all` and `make check` run without error.

### Step 1.8: Secrets Management (SOPS + Age)
*   **File/Path:** `.sops.yaml`
*   **Action:** Create
*   **Instruction:** Configure creation rules to use a local `keys.txt` (for dev) and AWS KMS (for prod if needed) to encrypt `.env` files.
*   **Verification:** `sops -e .env > .env.enc` works.

> **Commit Checkpoint:** "feat(infra): walking skeleton with docker-compose, makefile, and linting"

---

## Phase 2: Backend Core (Data, Auth & Compliance)
**Goal:** Production-ready backend with strict HIPAA controls: UUIDs, Role Separation, MFA, and Consent tracking.

### Step 2.1: Configuration with Pydantic Settings
*   **File/Path:** `backend/src/config.py`
*   **Action:** Create
*   **Instruction:** Use `pydantic-settings` to manage env vars (DB URL, Firebase Creds, etc.).
*   **File/Path:** `backend/src/http_client.py`
*   **Action:** Create
*   **Instruction:** Configure a shared `httpx` client with **10s default timeout** AND **domain whitelisting** for all external calls.
    ```python
    import httpx
    from urllib.parse import urlparse
    
    # SECURITY: Domain whitelist for all outbound HTTP requests
    # Prevents SSRF attacks and unauthorized data exfiltration
    ALLOWED_DOMAINS = {
        # AWS Services
        "s3.amazonaws.com",
        "s3.us-west-2.amazonaws.com",
        "sqs.us-west-2.amazonaws.com",
        "textract.us-west-2.amazonaws.com",
        "email.us-west-2.amazonaws.com",  # SES
        "connect.us-west-2.amazonaws.com",
        # Google/Firebase
        "identitytoolkit.googleapis.com",
        "securetoken.googleapis.com",
        "aiplatform.googleapis.com",
        # Allow wildcard for regional variants
    }
    
    def validate_url(url: str) -> bool:
        """Check if URL domain is in the allowlist."""
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        # Check exact match or subdomain match
        return any(
            host == domain or host.endswith(f".{domain}")
            for domain in ALLOWED_DOMAINS
        )
    
    class SafeAsyncClient(httpx.AsyncClient):
        """httpx client with domain whitelisting."""
        
        async def request(self, method: str, url: str, **kwargs):
            if not validate_url(str(url)):
                raise ValueError(f"Domain not whitelisted: {url}")
            return await super().request(method, url, **kwargs)
    
    # Default timeout for all external API calls (10 seconds)
    # Prevents hanging on slow third-party APIs
    http_client = SafeAsyncClient(
        timeout=httpx.Timeout(10.0, connect=5.0),
        follow_redirects=True,
    )
    ```
*   **Verification:** Verify env vars load correctly on startup. Attempt request to non-whitelisted domain -> `ValueError` raised.

### Step 2.2: Database Setup (Async SQLAlchemy)
*   **File/Path:** `backend/src/database.py`
*   **Action:** Create
*   **Instruction:** Configure `AsyncEngine` and `AsyncSession`. Ensure UUID support is enabled in Postgres dialect if needed (usually handled by `sqlalchemy.dialects.postgresql.UUID`).
*   **Verification:** Connect to the docker-compose postgres instance.

### Step 2.3: Migrations (Alembic)
*   **File/Path:** `backend/alembic.ini`
*   **Action:** Init
*   **Instruction:** Initialize alembic (`uv run alembic init -t async migrations`). Configure `env.py` to use `src.config.settings.DATABASE_URL`.
*   **Verification:** `uv run alembic revision --autogenerate -m "init"` creates a migration file.

### Step 2.4: Users, Profiles & Tenants
*   **File/Path:** `backend/src/models/` (multiple files)
*   **Action:** Create
*   **Instruction:**
    *   **Concept:** Separate Identity (User) from Role (Provider, Patient, Staff, Proxy) to allow:
        *   "Right to be Forgotten" (deletion of User) while retaining Clinical Records for compliance.
        *   A single email address to hold multiple roles (e.g., Patient at Clinic A and Provider at Clinic B).
        *   Multi-tenancy: Users can belong to 0-Many Organizations with strict data segregation.

    *   **Core Entities:**
        ```
        Organization (Tenant)
        ├── id (ULID)
        ├── name
        ├── tax_id
        └── settings_json
        
        User (Authentication Record)
        ├── id (ULID)
        ├── email (unique)
        ├── password_hash (nullable - OAuth users)
        ├── mfa_enabled (boolean)
        ├── fcm_device_tokens (Array[str])
        └── deleted_at (soft delete)
        
        AuditLog (Immutable)
        ├── id (ULID)
        ├── actor_id → User.id
        ├── target_resource
        ├── action_type
        ├── ip_address
        └── timestamp
        ```

    *   **Role Entities:**
        ```
        Provider (Licensed Clinician)
        ├── id (ULID)
        ├── user_id → User.id
        ├── npi_number (unique)
        ├── dea_number
        └── state_licenses (Array[{state, license_number, expiry}])
        
        Staff (Non-Provider Employee)
        ├── id (ULID)
        ├── user_id → User.id
        ├── employee_id
        └── job_title (enum: NURSE, BILLER, ADMIN, CALL_CENTER_AGENT)
        
        Patient (Care Receiver)
        ├── id (ULID)
        ├── user_id → User.id (nullable for Dependents)
        ├── mrn (Medical Record Number)
        ├── dob
        ├── legal_sex
        ├── gender_identity
        └── is_self_managed (boolean - False for Dependents)
        
        Proxy (Care Manager)
        ├── id (ULID)
        ├── user_id → User.id
        └── relationship_type (enum: PARENT, GUARDIAN, POA, SPOUSE)
        ```

    *   **Association Tables:**
        ```
        Organization_Member (User ↔ Organization)
        ├── id (ULID)
        ├── user_id → User.id
        ├── organization_id → Organization.id
        ├── role (enum: PROVIDER, STAFF, ADMIN)
        └── role_entity_id (→ Provider.id or Staff.id based on role)
        
        Patient_Proxy_Assignment (Proxy ↔ Patient, M:M)
        ├── id (ULID)
        ├── proxy_id → Proxy.id
        ├── patient_id → Patient.id
        ├── permissions_mask (JSON: {can_view_clinical, can_view_billing, can_schedule})
        ├── relationship_proof (nullable - document ID for POA verification)
        └── expires_at (nullable - for temporary access)
        
        Care_Team (Provider ↔ Patient within Organization)
        ├── id (ULID)
        ├── provider_id → Provider.id
        ├── patient_id → Patient.id
        ├── organization_id → Organization.id
        └── role (enum: PRIMARY, SPECIALIST, CONSULTANT)
        ```

    *   **Contact & Demographics:**
        ```
        Contact_Method
        ├── id (ULID)
        ├── user_id → User.id (nullable)
        ├── patient_id → Patient.id (nullable, for dependents)
        ├── type (enum: MOBILE, HOME, WORK, EMAIL)
        ├── value
        ├── is_primary (boolean)
        └── is_safe_for_voicemail (boolean - CRITICAL for patient safety)
        ```
        *   **Safe Contact Protocol:** Logic MUST prevent automated messages/voicemails to contacts where `is_safe_for_voicemail = False` (e.g., domestic violence situations).

    *   **CRITICAL:** All Primary Keys must use **ULID**.
    *   **CRITICAL:** All clinical data uses soft deletes (`deleted_at` timestamp) for legal retention.
*   **Verification:** Run migration. Verify all tables created with proper foreign keys and indexes.

### Step 2.5: Auth & GCIP Integration
*   **File/Path:** `backend/src/security/auth.py`
*   **Action:** Create
*   **Instruction:**
    *   **Provider:** Use Google Cloud Identity Platform (GCIP). It is API-compatible with Firebase SDK but enterprise-grade.
    *   Initialize `firebase-admin` (works with GCIP).
    *   Create dependencies:
        *   `get_current_user`: Decodes JWT.
        *   `get_auth_context`: Role-based access within Organization (via `Organization_Member`).
        *   `get_current_staff`: Enforces user has `Provider` or `Staff` role entity.
    *   **MFA:**
        *   Enforce MFA policies in the **GCP Console** for the "Staff" tenant/group.
        *   Middleware should verify the token's `auth_time` or MFA claims.
    *   **Email Handling:** Configure GCIP/Firebase Console to use AWS SES SMTP credentials.
*   **Verification:** Unit tests: Patient cannot access Staff route; Staff without MFA cannot access Staff route.

### Step 2.6: Secure Impersonation
*   **File/Path:** `backend/src/api/admin.py`
*   **Action:** Create
*   **Instruction:**
    *   Create Endpoint `POST /admin/impersonate/{patient_id}`.
        *   **Body:** `{"reason": "string"}` (Required).
    *   **Logic:**
        *   Verify caller is `ADMIN`.
        *   **Audit:** Log "Break Glass" event with `reason` to `audit_logs` table *before* generation.
        *   Generate a **Custom Token** (via firebase-admin) for the `patient_id`.
        *   **CRITICAL:** Add custom claims: `{"act_as": patient_id, "impersonator_id": admin_id}`.
    *   Returns the custom token.
*   **Verification:** Decode token to verify claims exist. Check database for "Break Glass" log entry.

### Step 2.7: Consent & Terms Tracking
*   **File/Path:** `backend/src/models/consent.py`
*   **Action:** Create
*   **Instruction:**
    *   Define `ConsentDocument` (type: [TOS, HIPAA], version: string, content: text).
    *   Define `UserConsent` (user_id, document_id, signed_at_ip, signed_at_timestamp).
    *   **TCPA Compliance:** Add boolean column `communication_consent_sms` to `User` or `PatientProfile` (default: False).
    *   **Logic:**
        *   Middleware/Dependency `verify_latest_consents`: Block API if critical docs (TOS/HIPAA) are unsigned.
        *   **SMS Service:** Check `communication_consent_sms` MUST be True before sending non-emergency messages.
*   **Verification:** User cannot access API until consent is recorded. Attempt to send SMS to opted-out user -> Error/Skip.

### Step 2.8: Internal Admin Panel (SQLAdmin)
*   **File/Path:** `backend/src/admin.py`
*   **Action:** Create
*   **Instruction:** Configure `sqladmin` for internal super-admin CRUD views.
    ```python
    from sqladmin import Admin, ModelView
    from src.database import engine
    from src.models import User, Patient, Provider, Staff, Organization
    
    admin = Admin(app, engine)
    
    class UserAdmin(ModelView, model=User):
        column_list = [User.id, User.email, User.mfa_enabled]
        can_delete = False  # HIPAA: Soft delete only
    
    class PatientAdmin(ModelView, model=Patient):
        column_exclude_list = [Patient.dob]  # Minimize PHI exposure
    
    class OrganizationAdmin(ModelView, model=Organization):
        column_list = [Organization.id, Organization.name, Organization.tax_id]
    
    admin.add_view(UserAdmin)
    admin.add_view(PatientAdmin)
    admin.add_view(OrganizationAdmin)
    ```
*   **Security:** SQLAdmin MUST be protected by `get_current_staff` dependency with `ADMIN` role check.
*   **Verification:** Access `/admin` as ADMIN -> see CRUD interface. Access as non-admin -> 403.

> **Commit Checkpoint:** "feat(backend): secure auth with mfa, uuids, and consent tracking"

---

## Phase 3: Frontend Foundations (App Logic)
**Goal:** Interactive UI with Authentication and API integration.

### Step 3.1: Shadcn UI Setup
*   **File/Path:** `frontend/components.json`
*   **Action:** Config
*   **Instruction:**
    *   Initialize shadcn-ui.
    *   Install validation dependencies: `pnpm add zod react-hook-form @hookform/resolvers`.
*   **Verification:** `npx shadcn-ui@latest add button` and `form` works.

### Step 3.2: API Type Generation (Static)
*   **File/Path:** `backend/scripts/generate_schema.py`
*   **Action:** Create
*   **Instruction:**
    *   **Goal:** Export `openapi.json` without connecting to the DB (which fails in CI).
    *   **Implementation:**
        *   Mock/Override `settings` (e.g., `DATABASE_URL="sqlite:///"`) *before* importing `src.main:app` or use `unittest.mock`.
        *   Ensure `on_startup` lifecycles (DB connect) are **NOT** run during this script execution.
    *   **Output:** Dump `json.dumps(app.openapi())` to `backend/openapi.json`.
*   **File/Path:** `frontend/package.json`
*   **Action:** Update
*   **Instruction:**
    *   Add `openapi-typescript` AND `openapi-zod-client`.
    *   Add `generate:types` script:
        ```bash
        cd ../backend && uv run python scripts/generate_schema.py && \
        cd ../frontend && \
        npx openapi-typescript ../backend/openapi.json -o src/lib/api-types.d.ts && \
        npx openapi-zod-client ../backend/openapi.json -o src/lib/api-schemas.ts
        ```
    *   **Benefit:** Synchronization. Backend Pydantic changes -> OpenAPI -> Frontend Types AND Zod Validation Schemas.
*   **Verification:** Run `pnpm generate:types`. Check `api-types.d.ts` and `api-schemas.ts` exist.

### Step 3.3: Firebase Client Auth
*   **File/Path:** `frontend/src/lib/firebase.ts`
*   **Action:** Create
*   **Instruction:** Initialize Firebase App with public config.
*   **File/Path:** `frontend/package.json`
*   **Action:** Update
*   **Instruction:** Add `react-firebase-hooks` for simplified auth state management.
    ```bash
    pnpm add firebase react-firebase-hooks
    ```
*   **File/Path:** `frontend/src/hooks/useAuth.ts`
*   **Action:** Create
*   **Instruction:** Create auth hook using `react-firebase-hooks`.
    ```typescript
    import { useAuthState, useSignInWithGoogle } from 'react-firebase-hooks/auth';
    import { auth } from '../lib/firebase';
    
    export function useAuth() {
      const [user, loading, error] = useAuthState(auth);
      const [signInWithGoogle, , googleLoading] = useSignInWithGoogle(auth);
      
      return {
        user,
        loading: loading || googleLoading,
        error,
        signInWithGoogle,
        signOut: () => auth.signOut(),
      };
    }
    ```
*   **Verification:** `console.log(auth)` and `useAuth()` hook returns auth state.

### Step 3.4: Async State Management
*   **File/Path:** `frontend/src/lib/query-client.ts`
*   **Action:** Create
*   **Instruction:**
    *   Install `@tanstack/react-query`.
    *   Setup `QueryClient`.
    *   Create a custom hook `useAuthQuery` that wraps the fetch call with the Firebase Token automatically.
*   **File/Path:** `frontend/src/stores/auth-store.ts`
*   **Action:** Create
*   **Instruction:** Create Zustand store for lightweight client-side state (auth flags, UI preferences).
    ```typescript
    import { create } from 'zustand';
    
    interface AuthStore {
      isAuthenticated: boolean;
      isLoading: boolean;
      userRole: 'PATIENT' | 'STAFF' | 'CALL_CENTER_AGENT' | null;
      setAuth: (auth: Partial<AuthStore>) => void;
    }
    
    export const useAuthStore = create<AuthStore>((set) => ({
      isAuthenticated: false,
      isLoading: true,
      userRole: null,
      setAuth: (auth) => set((state) => ({ ...state, ...auth })),
    }));
    ```
*   **Note:** Use Zustand for UI state only. TanStack Query handles all server state (API data).
*   **Verification:** Query client wraps the app. Zustand store updates on auth state change.

### Step 3.5: Role-Based Route Protection
*   **File/Path:** `frontend/src/routes/_auth.tsx` (TanStack Router)
*   **Action:** Create
*   **Instruction:**
    *   Create a layout that checks auth state AND user role (via `Organization_Member` lookup).
    *   **Loading State:** Return `<Skeleton />` or `null` while `auth.loading` is true. Do not render child routes until auth is resolved.
    *   Differentiate between `/_auth/patient` (redirects if not Patient or Proxy) and `/_auth/staff` (redirects if no Provider/Staff role).
    *   **Proxy Dashboard:** If user is a Proxy, show list of managed Patients (via `Patient_Proxy_Assignment`) to select.
    *   **Self-Managed Patient Dashboard:** If user has a Patient record with `is_self_managed = true`, show only their own view.
    *   **Dependent Patient:** Accessed only via Proxy selection. No direct login.
    *   Handle "Consent Required" redirect if API returns 403 Consent Missing.
*   **Verification:** Accessing staff dashboard as patient -> 403/Redirect.

> **Commit Checkpoint:** "feat(frontend): auth guards and api types"

### Step 3.6: Testing (Vitest + Playwright) & Data Seeding
*   **File/Path:** `frontend/vitest.config.ts`
*   **Action:** Create
*   **Instruction:** Configure Vitest for frontend unit testing.
    ```typescript
    import { defineConfig } from 'vitest/config';
    import react from '@vitejs/plugin-react';
    
    export default defineConfig({
      plugins: [react()],
      test: {
        environment: 'jsdom',
        globals: true,
        setupFiles: './src/test-setup.ts',
      },
    });
    ```
*   **File/Path:** `frontend/package.json`
*   **Action:** Update
*   **Instruction:** Add vitest as dev dependency: `pnpm add -D vitest @testing-library/react @testing-library/jest-dom jsdom`
*   **File/Path:** `backend/scripts/seed_e2e.py`
*   **Action:** Create
*   **Instruction:**
    *   Create script to **Wipe DB** and insert deterministic "Test Patient" and "Test Staff".
*   **File/Path:** `frontend/playwright.config.ts`
*   **Action:** Create
*   **Instruction:** 
    *   Configure Playwright to test against `localhost:5173`.
    *   **Hook:** Configure `globalSetup` (or `beforeAll`) to run `uv run python ../backend/scripts/seed_e2e.py`.
*   **Verification:** 
    *   **Unit:** `pnpm vitest run` passes.
    *   **E2E:** `pnpm exec playwright test` runs against the seeded data (e.g., login as "Test Patient" succeeds).

### Step 3.7: Mobile (Capacitor + PWA)
*   **File/Path:** `frontend/vite.config.ts`
*   **Action:** Config
*   **Instruction:**
    *   **Capacitor:** Initialize & Configure platforms.
    *   **PWA (Security Critical):** Configure `vite-plugin-pwa`.
        *   **Strategy:** Cache **App Shell Only** (HTML/JS/CSS/Fonts/Icons).
        *   **Network:** Use explicit **NetworkOnly** strategy for `/api/*` routes.
        *   **Constraint:** **Online Only.** Do NOT store PHI in LocalStorage, IndexedDB, or Unencrypted Cache. The app should not function for data access if offline. This eliminates the need for complex client-side encryption key management for the MVP.
        *   **Workbox Config (vite.config.ts):**
            ```typescript
            import { VitePWA } from 'vite-plugin-pwa';

            export default defineConfig({
              plugins: [
                VitePWA({
                  registerType: 'autoUpdate',
                  workbox: {
                    // Cache app shell assets only
                    globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
                    
                    // CRITICAL: NetworkOnly for ALL API routes
                    // Prevents caching of:
                    // - PHI data responses
                    // - 401/403 auth errors (would cause stale auth state)
                    // - Any dynamic content
                    runtimeCaching: [
                      {
                        urlPattern: /^https?:\/\/.*\/api\/.*/i,
                        handler: 'NetworkOnly',
                        options: {
                          // Do not cache ANY responses, including errors
                          networkTimeoutSeconds: 10,
                        },
                      },
                    ],
                    
                    // Explicitly exclude API from precache
                    navigateFallbackDenylist: [/^\/api/],
                  },
                }),
              ],
            });
            ```
    *   **Push Notifications:**
        *   Install `@capacitor/push-notifications`.
        *   Register with Firebase Cloud Messaging (FCM).
        *   **Sync:** On login, POST the FCM token to `POST /api/users/device-token`.
*   **Verification:** Build app. toggle "Offline" in DevTools. App loads (skeleton), but API calls fail safely (showing "No Internet" toast/state). Verify FCM token appears in backend DB on login.

---

## Phase 4: Shared Polish & Infrastructure
**Goal:** Logging, Audits, and Production Prep.

### Step 4.1: Performant PHI Masking & Structured Logging
*   **File/Path:** `backend/src/logging.py`
*   **Action:** Config
*   **Instruction:**
    *   Configure `structlog` to output JSON.
    *   **Production Format:** Use **single-line JSON** in production for CloudWatch parsing.
        ```python
        import structlog
        from src.config import settings
        
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),  # Single-line JSON
            ],
            wrapper_class=structlog.make_filtering_bound_logger(settings.LOG_LEVEL),
        )
        ```
    *   **Hot Path Strategy:** **Targeted Key Masking**. Redact specific keys (`password`, `access_token`, `ssn`) or allow-list safe keys.
    *   **Exception Strategy:** Run Presidio (NLP) *synchronously* ONLY on **uncaught exception tracebacks**.
        *   *Rationale:* Tracebacks contain unpredictable variable states. The performance cost is acceptable on crashes (rare).
    *   **DB Query Comment Injection:** Inject `request_id` into SQL queries for observability.
        ```python
        from sqlalchemy import event
        
        @event.listens_for(engine.sync_engine, "before_cursor_execute")
        def inject_query_comment(conn, cursor, statement, parameters, context, executemany):
            request_id = current_request_id.get()
            if request_id:
                # Prepend comment to query for tracing in slow query logs
                statement = f"/* request_id={request_id} */ {statement}"
            return statement, parameters
        ```
    *   Prohibit any raw logging to stdout.
*   **Verification:** Ensure sensitive keys in the API response do not appear in console logs. Raise an exception with a mocked credit card in a variable -> Verify traceback is masked. Check slow_log for request_id comments.

### Step 4.2: Audit Logging & Row Level Security (RLS)
*   **File/Path:** `backend/src/middleware/context.py`
*   **Action:** Create
*   **Instruction:**
    *   Create a `ContextMiddleware` (or use `starlette-context`) that captures `user_id` and `tenant_id` from the JWT (if present) and stores them in a `contextvar`.
*   **File/Path:** `backend/src/database.py`
*   **Action:** Update
*   **Instruction:**
    *   Use SQLAlchemy `event.listen(AsyncSession, 'after_begin')` to SET variables.
    *   **CRITICAL Safety:**
        1.  Use `set_config(..., is_local=True)` to scope to transaction.
        2.  **Strict Reset:** Add a listener for `pool` `checkin` to explicitly `DISCARD ALL` or RESET variables to prevent leakage in pgbouncer/pool.
    *   **Implementation:**
        ```python
        # =============================================================================
        # SESSION VARIABLE LIFECYCLE & POOL SAFETY
        # =============================================================================
        # 
        # WHY THIS MATTERS (HIPAA/SECURITY):
        # ----------------------------------
        # PostgreSQL session variables (set via `set_config`) persist for the lifetime
        # of a database CONNECTION, not a transaction. In async connection pools
        # (asyncpg, pgbouncer), connections are reused across different HTTP requests.
        #
        # WITHOUT proper cleanup, this creates a critical security vulnerability:
        #   1. Request A (Tenant X) sets `app.current_tenant_id = 'tenant-x'`
        #   2. Request A completes, connection returns to pool
        #   3. Request B (Tenant Y) grabs the SAME connection
        #   4. If Request B forgets to set variables, RLS policies use STALE values
        #   5. Tenant Y sees Tenant X's data → DATA BREACH
        #
        # THE TWO-LAYER DEFENSE:
        # ----------------------
        # Layer 1: `set_config(..., is_local=True)` 
        #   - Scopes variable to current TRANSACTION only
        #   - Automatically cleared on COMMIT/ROLLBACK
        #   - This is the PRIMARY defense
        #
        # Layer 2: `DISCARD ALL` on pool checkin
        #   - Belt-and-suspenders cleanup when connection returns to pool
        #   - Catches edge cases: timeouts, crashes, missed commits
        #   - Resets ALL session state: variables, prepared statements, temp tables
        #   - This is the BACKUP defense
        #
        # BOTH layers are required for defense-in-depth.
        # =============================================================================

        @event.listens_for(AsyncSession.sync_session_class, "after_begin")
        def set_session_context(session, transaction, connection):
            """
            Set RLS context variables at transaction start.
            
            The `is_local=True` (third param) scopes to this transaction only.
            Variables auto-clear on commit/rollback.
            """
            user_id = current_user_id.get()
            tenant_id = current_tenant_id.get()
            
            if tenant_id:
                connection.execute(text(
                    "SELECT set_config('app.current_tenant_id', :tid, true)"
                ), {"tid": str(tenant_id)})
            if user_id:
                connection.execute(text(
                    "SELECT set_config('app.current_user_id', :uid, true)"
                ), {"uid": str(user_id)})

        @event.listens_for(engine.sync_engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """
            CRITICAL: Reset ALL session state when connection returns to pool.
            
            This prevents cross-request leakage of:
            - Session variables (tenant_id, user_id)
            - Prepared statements
            - Temporary tables
            - Advisory locks
            
            Must be on sync_engine (not async) because checkin happens at DBAPI level.
            """
            cursor = dbapi_connection.cursor()
            cursor.execute("DISCARD ALL")
            cursor.close()
        ```
*   **File/Path:** `backend/migrations/versions/XXXX_add_audit_rls.py`
*   **Action:** Create
*   **Instruction:**
    *   **Audit:** Add raw SQL migration for `audit_logs` table & trigger.
    *   **Trigger Logic:** Record `actor_id` as `app.current_real_user_id` (the admin).
    *   **RLS:** Enable RLS on sensitive tables.
    *   **Policy:** `CREATE POLICY tenant_isolation ON patient_profile USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid);`
    *   **Note:** The `true` argument ensures it returns NULL (access denied) if variable is missing, rather than erroring or leaking.
*   **Verification:** Insert a user, check `audit_logs`. Access without auth -> effectively 0 rows visible.

### Step 4.2b: Read Access Auditing (Middleware)
*   **File/Path:** `backend/src/middleware/audit.py`
*   **Action:** Create
*   **Instruction:**
    *   **Goal:** Log *read* access to PHI by Staff, not just writes.
    *   **Logic:**
        *   Intercept all requests to `/api/staff/*`.
        *   Log event `READ_ACCESS` to `AuditService` (side effect, do not block response).
        *   Include: `actor_id`, `resource_path`, `query_params` (masked).
*   **Verification:** `GET /api/staff/patients/{id}` creates an entry in `audit_logs`.

### Step 4.3: OpenTofu AWS Setup
*   **File/Path:** `infra/aws/main.tf`
*   **Action:** Create
*   **Instruction:** Define S3 bucket (private, encrypted), ECR repositories, SES identity, and Secrets Manager for GCP credentials.
    *   **CRITICAL:** S3 bucket MUST be in the **same AWS region as Aptible** (us-east-1 or us-west-2) to minimize latency and data transfer costs.
*   **File/Path:** `infra/aws/ses.tf`
*   **Action:** Create
*   **Instruction:** Define AWS SES resources for transactional email.
    ```hcl
    # =============================================================================
    # AWS SES - Transactional Email
    # =============================================================================
    
    resource "aws_ses_domain_identity" "main" {
      domain = var.domain_name  # e.g., "lockdev.com"
    }
    
    resource "aws_ses_domain_dkim" "main" {
      domain = aws_ses_domain_identity.main.domain
    }
    
    # DKIM DNS records (add to Route53)
    resource "aws_route53_record" "ses_dkim" {
      count   = 3
      zone_id = aws_route53_zone.main.zone_id
      name    = "${aws_ses_domain_dkim.main.dkim_tokens[count.index]}._domainkey.${var.domain_name}"
      type    = "CNAME"
      ttl     = 600
      records = ["${aws_ses_domain_dkim.main.dkim_tokens[count.index]}.dkim.amazonses.com"]
    }
    
    # SPF record
    resource "aws_route53_record" "ses_spf" {
      zone_id = aws_route53_zone.main.zone_id
      name    = var.domain_name
      type    = "TXT"
      ttl     = 600
      records = ["v=spf1 include:amazonses.com ~all"]
    }
    
    # DMARC record
    resource "aws_route53_record" "ses_dmarc" {
      zone_id = aws_route53_zone.main.zone_id
      name    = "_dmarc.${var.domain_name}"
      type    = "TXT"
      ttl     = 600
      records = ["v=DMARC1; p=quarantine; rua=mailto:dmarc@${var.domain_name}"]
    }
    
    # Verified email identity for sending
    resource "aws_ses_email_identity" "noreply" {
      email = "noreply@${var.domain_name}"
    }
    ```
*   **File/Path:** `infra/aws/secrets.tf`
*   **Action:** Create
*   **Instruction:** Store GCP service account JSON in AWS Secrets Manager for secure retrieval.
    ```hcl
    # =============================================================================
    # AWS SECRETS MANAGER - GCP Service Account
    # =============================================================================
    # Stores the GOOGLE_SERVICE_ACCOUNT_JSON for Firebase Admin SDK
    # This enables GCIP (Google Cloud Identity Platform) integration
    
    resource "aws_secretsmanager_secret" "gcp_service_account" {
      name        = "lockdev/gcp-service-account"
      description = "GCP Service Account JSON for Firebase Admin SDK (Identity Platform)"
      
      tags = {
        Environment = var.environment
        ManagedBy   = "opentofu"
      }
    }
    
    # The actual secret value is set manually or via CI:
    # aws secretsmanager put-secret-value \
    #   --secret-id lockdev/gcp-service-account \
    #   --secret-string file://service-account.json
    
    # IAM policy for backend to read the secret
    resource "aws_iam_policy" "read_gcp_secret" {
      name        = "lockdev-read-gcp-secret"
      description = "Allow reading GCP service account secret"
      
      policy = jsonencode({
        Version = "2012-10-17"
        Statement = [{
          Effect   = "Allow"
          Action   = ["secretsmanager:GetSecretValue"]
          Resource = aws_secretsmanager_secret.gcp_service_account.arn
        }]
      })
    }
    ```
*   **Backend Integration:** Update `backend/src/config.py` to fetch from Secrets Manager in production:
    ```python
    import boto3
    import json
    from pydantic_settings import BaseSettings
    
    def get_gcp_credentials() -> dict | None:
        """Fetch GCP service account from AWS Secrets Manager (prod only)."""
        if settings.ENVIRONMENT == "development":
            return None  # Use local file or GOOGLE_APPLICATION_CREDENTIALS
        
        client = boto3.client("secretsmanager", region_name="us-west-2")
        response = client.get_secret_value(SecretId="lockdev/gcp-service-account")
        return json.loads(response["SecretString"])
    ```
    *   **Log Drain Target:** Configure the S3 bucket as a target for Aptible log drain (JSON logs from structlog).
*   **State Backend (REQUIRED for team/CI):**
    *   **File/Path:** `infra/aws/backend.tf`
    *   **Action:** Create
    *   **Instruction:** Configure remote state with S3 + DynamoDB locking to prevent concurrent modifications.
        ```hcl
        # =============================================================================
        # REMOTE STATE BACKEND
        # =============================================================================
        # Why this matters:
        # - Local state files get lost, corrupted, or cause merge conflicts
        # - Without locking, two CI runs can corrupt state simultaneously
        # - S3 provides durability, DynamoDB provides atomic locking
        # =============================================================================

        terraform {
          backend "s3" {
            bucket         = "lockdev-tf-state"
            key            = "aws/terraform.tfstate"
            region         = "us-west-2"
            encrypt        = true
            dynamodb_table = "lockdev-tf-locks"
          }
        }
        ```
    *   **Bootstrap (One-Time Setup):**
        ```bash
        # Create state bucket and lock table BEFORE running `tofu init`
        # This is a chicken-and-egg: can't use Tofu to create its own backend
        
        aws s3api create-bucket \
          --bucket lockdev-tf-state \
          --region us-west-2 \
          --create-bucket-configuration LocationConstraint=us-west-2

        aws s3api put-bucket-versioning \
          --bucket lockdev-tf-state \
          --versioning-configuration Status=Enabled

        aws s3api put-bucket-encryption \
          --bucket lockdev-tf-state \
          --server-side-encryption-configuration '{
            "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
          }'

        aws dynamodb create-table \
          --table-name lockdev-tf-locks \
          --attribute-definitions AttributeName=LockID,AttributeType=S \
          --key-schema AttributeName=LockID,KeyType=HASH \
          --billing-mode PAY_PER_REQUEST \
          --region us-west-2
        ```
*   **Verification:** `tofu init` succeeds and shows "Initializing the backend..." with S3. `tofu plan` shows resources.

### Step 4.4: Background Worker (ARQ + Redis)
*   **File/Path:** `backend/src/worker.py`
*   **Action:** Create
*   **Instruction:**
    *   Define `WorkerSettings` class.
    *   Configure `functions` list (start with a simple `health_check_task`).
    *   Configure `on_startup` / `on_shutdown` to handle DB/Redis connections.
    *   **Idempotent Execution:** All tasks MUST be idempotent to handle retries safely.
        ```python
        from arq import create_pool
        from arq.connections import RedisSettings
        
        async def process_document_job(ctx, document_id: str):
            """Idempotent: Check if already processed before running."""
            async with get_db_session() as db:
                doc = await db.get(Document, document_id)
                if doc.processing_status == "COMPLETED":
                    return {"status": "already_processed"}  # Skip
                
                # Process document...
                doc.processing_status = "COMPLETED"
                await db.commit()
            return {"status": "success"}
        
        class WorkerSettings:
            functions = [process_document_job]
            redis_settings = RedisSettings()
            max_jobs = 10
            job_timeout = 300  # 5 minutes
        ```
*   **Verification:** `uv run arq src.worker.WorkerSettings` starts successfully.

### Step 4.5: Aptible Procfile & Deployment
*   **File/Path:** `Procfile`
*   **Action:** Create
*   **Instruction:** Define remote process types.
    ```text
    web: uv run uvicorn src.main:app --host 0.0.0.0 --port $PORT
    worker: uv run arq src.worker.WorkerSettings
    release: uv run alembic upgrade head
    ```
*   **File/Path:** `.github/workflows/deploy.yml`
*   **Action:** Create
*   **Instruction:**
    *   **Decrypt Secrets:**
        *   Install `sops` in the runner.
        *   Decode `.env.enc` -> `.env` using `SOPS_AGE_KEY` (Github Secret).
    *   **Config Sync (Critical for Aptible):**
        *   Install Aptible CLI.
        *   Run `aptible config:set --app "$APTIBLE_APP" $(cat .env | xargs)` to inject secrets *before* code deploy.
    *   **Deploy Code:**
        *   Push to Aptible git remote.
*   **Verification:** Dry run locally using `honcho start`. Verify `git push` triggers build AND secrets are present in Aptible dashboard.

### Step 4.6: DNS & Certificates (Route53 + Aptible)
*   **File/Path:** `infra/aws/route53.tf`
*   **Action:** Create
*   **Instruction:**
    *   Define AWS Route53 Hosted Zone for the domain.
    *   Add TXT records for SES verification (DMARC/DKIM/SPF).
    *   Add logic to output the Nameservers to configure at the Registrar level.
*   **File/Path:** `Aptible Dashboard (Manual Step)`
*   **Action:** Config
*   **Instruction:**
    *   Provision Managed TLS endpoints for `app` and `api` services.
    *   Copy the Validation CNAME values from Aptible.
    *   Add CNAME records to Route53 to complete validation.
*   **Verification:** `dig +short app.domain.com` returns Aptible ELB address.

### Step 4.7: Policy as Code (Checkov)
*   **File/Path:** `.github/workflows/infra-scan.yml`
*   **Action:** Create
*   **Instruction:** Add a GitHub Action to run `checkov -d infra` on PRs.
*   **Verification:** Run action on dummy TF file with an issue (e.g. unencrypted S3).

> **Commit Checkpoint:** "feat(infra): secure logging, audit triggers, dns setup, and prod configuration"

---

## Phase 5: Service Integrations & Features
**Goal:** Explicit scaffolding for all external APIs and specific feature requirements.

### Step 5.1: AI Service (Vertex AI SDK)
*   **File/Path:** `backend/src/services/ai.py`
*   **Action:** Create
*   **Instruction:**
    *   Initialize `vertexai` client using `google-auth`.
    *   **Logic:**
        *   Use `vertexai.generative_models.GenerativeModel("gemini-1.5-pro")`.
        *   Define Pydantic models for expected responses (Response Schemas).
        *   Use `model.generate_content(..., generation_config={"response_mime_type": "application/json", "response_schema": MyPydanticModel})`.
        *   **Constraint:** "Zero Data Retention" settings must be enabled in the Platform/Request config if available, or ensured via BAA.
    *   Create a simple `summarize_text(text: str)` function as a smoke test.
*   **Verification:** Unit test mocking VertexAI returns expected response.

### Step 5.2: Telephony & Messaging (AWS)
*   **File/Path:** `backend/src/services/telephony.py`
*   **Action:** Create
*   **Instruction:**
    *   Initialize `boto3` clients for `connect` (Amazon Connect) and `pinpoint-sms-voice-v2` (End User Messaging).
    *   **SMS:** Create `send_sms(to, body)` using AWS End User Messaging.
    *   **Voice:** Create `initiate_outbound_call(to, contact_flow_id)` using Amazon Connect.
    *   **Safeguard:** Ensure `to` numbers are validated and masked in all logs.
*   **Verification:** Send test SMS from AWS Console (Sandbox) or via REPL. Initiate a test call flow.

### Step 5.3: Document Processing (AWS Textract)
*   **File/Path:** `backend/src/services/documents.py`
*   **Action:** Create
*   **Instruction:**
    *   **Goal:** Async processing of uploaded documents.
    *   **API:** create `generate_upload_url(filename)` returning a Presigned S3 URL.
    *   **Worker:** Create `process_document_job` task in `backend/src/worker.py`.
        *   Triggered manually (API) or via S3 Event.
        *   Calls AWS Textract `start_document_text_detection` (Async API) or `detect_document_text` (Sync API, but inside the worker).
*   **Verification:** Upload file -> Enqueue Job -> Text extracted and saved to DB.

### Step 5.3b: Virus Scanning (AWS Lambda on S3 Upload)
*   **File/Path:** `infra/aws/lambda-virus-scan.tf`
*   **Action:** Create
*   **Instruction:** Deploy Lambda function triggered on S3 PutObject events for virus scanning.
    *   **Logic:**
        *   Trigger on `s3:ObjectCreated:*` events in the documents bucket.
        *   Use ClamAV layer (pre-built) or Amazon GuardDuty Malware Protection.
        *   On detection: Move file to quarantine bucket, log to CloudWatch, alert via SNS.
        *   On clean: Tag object with `scan-status=clean`.
    *   **Worker Integration:** Backend worker should check `scan-status` tag before processing.
    ```hcl
    resource "aws_lambda_function" "virus_scan" {
      function_name = "lockdev-virus-scan"
      runtime       = "python3.11"
      handler       = "handler.lambda_handler"
      layers        = [aws_lambda_layer_version.clamav.arn]
      timeout       = 300
      memory_size   = 1024
    }
    
    resource "aws_s3_bucket_notification" "scan_trigger" {
      bucket = aws_s3_bucket.documents.id
      lambda_function {
        lambda_function_arn = aws_lambda_function.virus_scan.arn
        events              = ["s3:ObjectCreated:*"]
      }
    }
    ```
*   **Verification:** Upload test EICAR file -> verify it's moved to quarantine bucket.

### Step 5.4: Real-Time Updates (SSE)
*   **File/Path:** `backend/src/api/events.py`
*   **Action:** Create
*   **Instruction:**
    *   Create an `EventGenerator` using `asyncio.Queue`.
    *   Expose `GET /api/events` endpoint using `StreamingResponse`.
    *   Implement Redis Pub/Sub listener to broadcast worker events to SSE clients.
*   **Verification:** Connect `curl -N http://localhost:8000/api/events` and trigger a dummy event.

### Step 5.5: Observability (CloudWatch & Structlog)
*   **File/Path:** `backend/src/main.py`
*   **Action:** Update
*   **Instruction:**
    *   Ensure `structlog` is configured to emit clean JSON to stdout.
    *   Aptible will capture stdout and forward to the configured log drain (AWS CloudWatch or S3).
    *   **Verification:** Verify logs in Aptible Dashboard or AWS CloudWatch appear as parsed JSON fields, not text blobs.

> **Commit Checkpoint:** "feat(backend): ai, twilio, textract, and sse integrations"

---

## Phase 6: Architecture Documentation
**Goal:** Maintain living documentation using Architecture as Code.

### Step 6.1: C4 Model (Structurizr)
*   **File/Path:** `docs/architecture/workspace.dsl`
*   **Action:** Create
*   **Instruction:** Define C4 models for L1 (System Context) and L2 (Container) diagrams using Structurizr DSL.
    ```dsl
    workspace "Lockdev" "Healthcare SaaS Platform" {
        model {
            patient = person "Patient" "End user accessing health data"
            staff = person "Staff" "Healthcare professional/Admin"
            callAgent = person "Call Center Agent" "Handles patient calls"
            
            lockdev = softwareSystem "Lockdev Platform" {
                spa = container "SPA" "React + TanStack" "TypeScript"
                api = container "API" "FastAPI" "Python"
                worker = container "Worker" "ARQ" "Python"
                db = container "Database" "PostgreSQL" "SQL"
                cache = container "Cache" "Redis" "NoSQL"
            }
            
            patient -> spa "Uses"
            staff -> spa "Uses"
            callAgent -> spa "Uses"
            spa -> api "HTTPS/JSON"
            api -> db "Reads/Writes"
            api -> cache "Session/Rate Limit"
            worker -> db "Background Jobs"
        }
        
        views {
            systemContext lockdev "L1-Context" {
                include *
                autoLayout
            }
            container lockdev "L2-Container" {
                include *
                autoLayout
            }
        }
    }
    ```
*   **Verification:** `structurizr-cli export -w workspace.dsl -format plantuml` generates diagrams.

### Step 6.2: D2 Diagrams (User Journey)
*   **File/Path:** `docs/architecture/user-journey.d2`
*   **Action:** Create
*   **Instruction:** Define user journey and process mapping diagrams using D2.
    ```d2
    # Patient Onboarding Flow
    patient: Patient
    app: Mobile App
    api: Backend API
    firebase: Firebase Auth
    consent: Consent Screen
    dashboard: Patient Dashboard
    
    patient -> app: Opens App
    app -> firebase: Authenticate
    firebase -> app: JWT Token
    app -> api: GET /api/user/me
    api -> app: {requires_consent: true}
    app -> consent: Show ToS/HIPAA
    consent -> api: POST /api/consent
    api -> app: {ok: true}
    app -> dashboard: Redirect
    ```
*   **Verification:** `d2 user-journey.d2 user-journey.svg` generates SVG.

### Step 6.3: OpenAPI (Auto-Generated)
*   **Note:** OpenAPI is auto-generated from FastAPI endpoints (see Step 3.2).
*   **Verification:** Access `/docs` (Swagger UI) or `/redoc` (ReDoc) on the running API.

> **Commit Checkpoint:** "docs: add c4 and d2 architecture diagrams"

---

## Appendix: Quick Reference — Session Variable Safety

For future implementers, here's the complete pattern for async-safe RLS:

```python
# database.py

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from contextvars import ContextVar

# Store request context
current_user_id: ContextVar[str | None] = ContextVar("current_user_id", default=None)
current_tenant_id: ContextVar[str | None] = ContextVar("current_tenant_id", default=None)

engine = create_async_engine(settings.DATABASE_URL)

@event.listens_for(AsyncSession.sync_session_class, "after_begin")
def set_rls_context(session, transaction, connection):
    """Set Postgres session variables within transaction scope."""
    user_id = current_user_id.get()
    tenant_id = current_tenant_id.get()
    if tenant_id:
        connection.execute(text(
            "SELECT set_config('app.current_tenant_id', :tid, true)"
        ), {"tid": str(tenant_id)})
    if user_id:
        connection.execute(text(
            "SELECT set_config('app.current_user_id', :uid, true)"
        ), {"uid": str(user_id)})

@event.listens_for(engine.sync_engine, "checkin")
def reset_on_checkin(dbapi_connection, connection_record):
    """CRITICAL: Prevent RLS context leakage between requests."""
    cursor = dbapi_connection.cursor()
    cursor.execute("DISCARD ALL")
    cursor.close()
```

This pattern ensures:
1. Variables are transaction-scoped (`is_local=true`)
2. Variables are wiped on pool return (`DISCARD ALL`)
3. No cross-request tenant leakage is possible
