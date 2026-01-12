# Comprehensive Security Audit Prompt for Claude

**Role:** You are a Principal Security Architect and HIPAA Compliance Expert with 20+ years of experience in securing multi-tenant healthcare SaaS platforms. You specialize in Python (FastAPI), TypeScript (React), PostgreSQL, AWS infrastructure, and healthcare compliance (HIPAA, HITECH).

**Objective:** Conduct a comprehensive white-box security audit of the entire `lockdev-saas-starter` codebase to identify vulnerabilities, compliance gaps, architectural weaknesses, and security enhancements. This is a HIPAA-compliant healthcare platform handling Protected Health Information (PHI) with multi-tenant architecture.

**Target Scope:**
- **Backend:** `apps/backend/src/` (FastAPI, SQLAlchemy, Firebase Auth, PostgreSQL)
- **Frontend:** `apps/frontend/src/` (React, TypeScript, TanStack Router/Query)
- **Infrastructure:** `infra/aws/` (OpenTofu/Terraform for AWS resources)
- **Database:** `apps/backend/migrations/` (Alembic migrations, RLS policies)
- **Configuration:** Docker, GitHub Actions, environment configs
- **Background Workers:** `apps/backend/src/worker.py` (ARQ)

---

## 1. Authentication & Identity Management

**Focus Areas:** `apps/backend/src/security/auth.py`, `apps/backend/src/api/users.py`, `apps/frontend/src/components/auth-guard.tsx`

### Critical Security Checks:

#### 1.1 Firebase/GCIP Token Verification
- **JWT Validation:** Analyze `verify_token()` dependency in `auth.py`
  - Are `aud` (audience), `iss` (issuer), and `sub` (subject) claims strictly validated?
  - Is token revocation check enabled (`check_revoked=True`)?
  - Are signing keys properly managed and rotated?
  - Can expired or malformed tokens be accepted?

- **Mock Authentication:** Review lines 70-86 in `auth.py`
  - Is mock authentication properly restricted to local environment only?
  - Can the `ENVIRONMENT` setting be bypassed or spoofed?
  - Is there sufficient logging of mock auth usage?

#### 1.2 Session Management
- **Session Creation:** Review `get_or_create_session()` in `auth.py`
  - Are sessions properly tracked in `UserSession` table?
  - Is there a maximum session duration enforced (15-minute idle timeout)?
  - Are concurrent sessions limited per user?

- **Session Revocation:** Check session termination logic
  - Does revoking a session actually invalidate the JWT?
  - Is there a token blacklist or short expiry mechanism?
  - Are all user sessions revoked on password change?

#### 1.3 Multi-Factor Authentication (MFA)
- **MFA Enforcement:** Search for `@requires_mfa` decorators and MFA validation
  - Is MFA strictly enforced for STAFF, PROVIDER, and ADMIN roles before PHI access?
  - Can users bypass MFA during setup or enrollment?
  - Are TOTP secrets properly encrypted in `mfa_secrets` table?
  - Is there a rate limit on MFA verification attempts?

#### 1.4 Impersonation ("Break Glass")
- **Impersonation Flow:** Review `apps/backend/src/api/admin.py` impersonation logic
  - Is the `act_as` claim cryptographically bound to the JWT?
  - Is impersonation time-limited (max 1 hour)?
  - Does it require a documented reason?
  - Is the `impersonator_id` captured in audit logs for all impersonated actions?
  - Can an ADMIN impersonate a SUPER_ADMIN?
  - Are there alerts for impersonation usage?

---

## 2. Authorization & Multi-Tenancy (IDOR Prevention)

**Focus Areas:** `apps/backend/src/database.py`, `apps/backend/src/security/org_access.py`, `apps/backend/src/middleware/context.py`, migrations with RLS

### Critical Security Checks:

#### 2.1 Row Level Security (RLS)
- **RLS Implementation:** Inspect `apps/backend/migrations/versions/f47bf61a922e_audit_and_rls.py`
  - Are RLS policies created for ALL tenant-scoped tables (Organizations, Patients, Appointments, etc.)?
  - Do policies enforce `organization_id` filtering?
  - Are policies tested for both SELECT, INSERT, UPDATE, and DELETE operations?

- **Session Context Setup:** Review `database.py` lines 58-74
  - Is `app.current_tenant_id` reliably set for EVERY authenticated request?
  - Are ContextVars (`tenant_id_ctx`, `user_id_ctx`) properly scoped to request lifecycle?
  - Can session variables be spoofed via malicious headers?
  - Is `set_config()` using parameterized queries to prevent SQL injection?

- **Connection Pool Security:** Check `receive_checkin()` event listener (lines 42-54)
  - Does `RESET ALL` properly clear session variables on connection return?
  - Is there a risk of session variable leakage between requests?

#### 2.2 Insecure Direct Object References (IDOR)
- **Endpoint Authorization:** Audit ALL API endpoints in `apps/backend/src/api/`
  - Do endpoints like `GET /patients/{id}`, `GET /appointments/{id}` verify ownership?
  - Are path parameters validated against `current_user.organization_id`?
  - Search for queries missing `where(organization_id=...)` clauses
  - Are JOIN queries properly filtered to prevent cross-tenant data access?

- **Query Patterns:** Use Grep to find potential issues:
  ```
  Pattern: select\(.*\)\.where\((?!.*organization_id)
  Files: apps/backend/src/api/*.py, apps/backend/src/services/*.py
  ```

#### 2.3 Role-Based Access Control (RBAC)
- **Frontend Guards:** Review `apps/frontend/src/components/auth-guard.tsx`
  - Are role checks enforced client-side AND server-side?
  - Can users manipulate frontend to access unauthorized routes?

- **Backend Dependencies:** Check role-based dependencies
  - Are endpoints decorated with proper role requirements?
  - Can a STAFF member access PROVIDER-only endpoints?
  - Can a PROVIDER modify ADMIN resources?
  - Is principle of least privilege followed?

#### 2.4 Organization Switching
- **Context Switching:** Review organization switching logic
  - Are users properly re-authenticated when switching orgs?
  - Are all cached data cleared on org switch?
  - Is there CSRF protection on org switch endpoints?

---

## 3. Data Privacy & HIPAA Compliance

**Focus Areas:** `apps/backend/src/logging.py`, `apps/backend/src/middleware/audit.py`, `apps/backend/src/models/audit.py`

### Critical Security Checks:

#### 3.1 PHI Leakage Prevention
- **Logging Security:** Audit `apps/backend/src/logging.py`
  - Is Presidio PII masking properly configured and active?
  - Are all PII recognizers (SSN, email, phone, names) enabled?
  - Is the fallback behavior safe if Presidio fails?
  - Search codebase for dangerous patterns:
    - `print()` statements in production code
    - `console.log()` in frontend
    - Unstructured logger calls that might dump model objects
    - Exception handlers that log full tracebacks with PHI

- **Response Sanitization:** Check API responses
  - Are Pydantic models properly configured to exclude sensitive fields?
  - Is PHI ever included in query parameters or URLs?
  - Are error messages sanitized to avoid PHI leakage?

#### 3.2 Audit Trail & Compliance
- **Audit Middleware:** Review `apps/backend/src/middleware/audit.py`
  - Does it capture ALL read access to PHI tables (Patients, Appointments, Clinical Notes)?
  - Are write operations (CREATE, UPDATE, DELETE) audited?
  - Is the `impersonator_id` captured when applicable?
  - Are audit logs truly immutable (no UPDATE/DELETE on audit_logs table)?

- **PostgreSQL Triggers:** Check database migrations for audit triggers
  - Are triggers created for automatic audit logging?
  - Do triggers capture old and new values for UPDATE operations?
  - Are triggers resilient to errors (won't block legitimate operations)?

- **Audit Log Retention:** Verify retention policy
  - Are audit logs retained for required period (6 years for HIPAA)?
  - Are audit logs backed up separately from operational data?
  - Is there protection against audit log tampering?

#### 3.3 Data Retention & Right to be Forgotten
- **Soft Deletes:** Verify soft-delete implementation
  - Do ALL clinical tables use `deleted_at` timestamp instead of hard deletes?
  - Are soft-deleted records excluded from normal queries?
  - Is there a process for permanent deletion after retention period?

- **Data Export:** Check patient data export functionality
  - Can patients request complete data export (Right of Access)?
  - Is exported data properly sanitized and formatted?
  - Is export access logged in audit trail?

#### 3.4 Encryption
- **Data at Rest:** Review infrastructure configuration
  - Is PostgreSQL encryption enabled?
  - Is S3 bucket encryption configured (check `infra/aws/`)?
  - Are Redis caches encrypted if they contain PHI?
  - Are database backups encrypted?

- **Data in Transit:** Check TLS/SSL configuration
  - Is HTTPS enforced for all endpoints?
  - Are strong TLS versions required (TLS 1.2+)?
  - Is certificate validation strict?
  - Check `TrustedHostMiddleware` configuration in `main.py`

---

## 4. Input Validation & Injection Prevention

**Focus Areas:** `apps/backend/src/schemas/`, `apps/backend/src/database.py`, `apps/frontend/src/`

### Critical Security Checks:

#### 4.1 SQL Injection
- **Raw SQL Usage:** Search for dangerous patterns
  - Look for `text()` usage in SQLAlchemy with string interpolation
  - Check if f-strings are used for SQL construction
  - Verify all parameters are bound using `:param` syntax
  - Review complex queries in services and repositories

- **Dynamic Query Building:** Audit query construction
  - Are WHERE clauses built securely?
  - Are ORDER BY columns validated against whitelist?
  - Are LIMIT/OFFSET values properly validated?

#### 4.2 Backend Input Validation
- **Pydantic Schemas:** Review `apps/backend/src/schemas/`
  - Are all API inputs validated through Pydantic v2 models?
  - Is `extra='forbid'` set to prevent mass assignment?
  - Are string lengths limited to prevent DoS?
  - Are regex patterns safe (no ReDoS vulnerabilities)?
  - Are email, phone, and other formats strictly validated?

- **Type Safety:** Check for weak typing
  - Search for `Any` types in schemas
  - Are enums used for fixed value sets?
  - Are UUIDs properly validated?

#### 4.3 Frontend Input Validation
- **Zod Schemas:** Review frontend validation
  - Are all form inputs validated with Zod schemas?
  - Do Zod schemas match backend Pydantic schemas?
  - Are error messages safe (no data leakage)?

- **XSS Prevention:** Check React components
  - Search for `dangerouslySetInnerHTML` usage
  - Are user-generated content (notes, messages) properly sanitized?
  - Is Content Security Policy (CSP) configured?
  - Are inline scripts prevented?

#### 4.4 File Upload Security
- **Document Upload:** Review `apps/backend/src/api/documents.py` and `apps/backend/src/services/documents.py`
  - Are file types strictly validated (whitelist, not blacklist)?
  - Is file size limited to prevent DoS?
  - Are filenames sanitized to prevent path traversal?
  - Is virus scanning integrated (check for ClamAV or similar)?
  - Are files stored outside webroot?
  - Are S3 pre-signed URLs time-limited?

---

## 5. Infrastructure & Cloud Security

**Focus Areas:** `infra/aws/`, `docker-compose.yml`, `.github/workflows/`, `Dockerfile`

### Critical Security Checks:

#### 5.1 AWS Infrastructure (OpenTofu)
- **S3 Bucket Security:** Review `infra/aws/s3.tf`
  - Are buckets private (no `acl = "public-read"`)?
  - Is server-side encryption enabled (AES-256 or KMS)?
  - Is versioning enabled for critical buckets?
  - Are bucket policies restrictive?
  - Is public access explicitly blocked?

- **IAM Policies:** Review `infra/aws/iam.tf`
  - Are policies following least privilege principle?
  - Are there any wildcard permissions (`Action: "*"`, `Resource: "*"`)?
  - Are service accounts scoped to specific resources?
  - Are IAM credentials properly rotated?

- **Network Security:** Check VPC and security group configs
  - Are databases accessible only from application tier?
  - Is Redis exposed to public internet?
  - Are security groups restrictive?

#### 5.2 Secret Management
- **Secrets in Code:** Scan for hardcoded secrets
  - Check `.env`, `.env.example`, `config.py` for hardcoded values
  - Are production secrets only in SOPS-encrypted files?
  - Search for patterns: API keys, passwords, tokens in code
  - Is `.env` properly in `.gitignore`?

- **SOPS Configuration:** Review `.sops.yaml`
  - Are encryption keys properly managed?
  - Is Age encryption correctly configured?
  - Are secrets encrypted before commit?

#### 5.3 Container Security
- **Dockerfile Security:** Review `apps/backend/Dockerfile` and `apps/frontend/Dockerfile`
  - Are containers running as non-root user?
  - Are base images pinned to SHA digests (not just tags)?
  - Are vulnerable packages updated?
  - Is multi-stage build used to minimize attack surface?
  - Are unnecessary tools removed from production images?

- **Docker Compose:** Review `docker-compose.yml`
  - Are default passwords changed for PostgreSQL/Redis?
  - Are ports properly restricted?
  - Are volumes properly scoped?
  - Is `docker-compose.yml` safe for production use?

#### 5.4 CI/CD Security
- **GitHub Actions:** Review `.github/workflows/`
  - Are secrets properly managed via GitHub Secrets?
  - Are third-party actions pinned to specific versions?
  - Is code scanning enabled (CodeQL, Dependabot)?
  - Are deployment keys properly scoped?
  - Is there protection against malicious PRs?

---

## 6. Business Logic & Application Security

**Focus Areas:** `apps/backend/src/services/`, `apps/backend/src/api/`

### Critical Security Checks:

#### 6.1 Race Conditions & Concurrency
- **Appointment Booking:** Review appointment scheduling logic
  - Can two users book the same time slot simultaneously?
  - Are database locks used (`SELECT ... FOR UPDATE`)?
  - Are optimistic locking or version fields used?
  - Is there transaction isolation to prevent dirty reads?

- **Critical State Transitions:** Check state machines
  - Are status changes atomic?
  - Can intermediate states be bypassed?
  - Are there validation checks on state transitions?

#### 6.2 Rate Limiting & DoS Prevention
- **SlowAPI Configuration:** Review `main.py` and rate limiting
  - Are sensitive endpoints (auth, PHI access) rate-limited?
  - Are limits appropriate for legitimate use?
  - Are rate limits enforced per user or per IP?
  - Is there protection against distributed DoS?

- **Resource Exhaustion:** Check for DoS vectors
  - Are pagination limits enforced on list endpoints?
  - Are query result sizes limited?
  - Are background jobs queued with limits?
  - Is there protection against regex DoS (ReDoS)?

#### 6.3 Business Logic Flaws

**Patient Safety:**
- **Safe Contact Protocol:** Review `apps/backend/src/services/messaging.py`, `apps/backend/src/services/notifications.py`
  - Is `is_safe_for_voicemail` flag ALWAYS checked before sending sensitive messages?
  - Are SMS/voice notifications validated for consent?
  - Is there a mechanism to prevent accidental PHI disclosure?

**Billing & Subscriptions:**
- **Payment State:** Review `apps/backend/src/services/billing.py` and webhook handling
  - Can users access paid features after subscription cancellation?
  - Are webhook signatures validated (Stripe)?
  - Is there protection against replay attacks on webhooks?
  - Are subscription states properly synchronized?

**Proxy/Guardian Access:**
- **Permission Enforcement:** Review proxy access logic
  - Are proxy permissions (`can_view_clinical`, `can_view_billing`, `can_schedule`) properly enforced?
  - Can a proxy escalate their own permissions?
  - Are proxy assignments validated (relationship proof)?
  - Is there protection against unauthorized proxy assignment?

#### 6.4 AI/LLM Security
- **Vertex AI Integration:** Review `apps/backend/src/services/ai.py`
  - Is zero data retention configured for LLM API?
  - Is PHI/PII scrubbed BEFORE sending to LLM?
  - Is the re-hydration pipeline secure?
  - Are prompts sanitized to prevent injection attacks?
  - Are LLM responses validated before use?
  - Is there rate limiting on AI service calls?

---

## 7. API & Network Security

**Focus Areas:** `apps/backend/src/main.py`, `apps/backend/src/http_client.py`, `apps/frontend/src/lib/axios.ts`

### Critical Security Checks:

#### 7.1 CORS Configuration
- **CORSMiddleware:** Review CORS settings in `main.py`
  - Are allowed origins explicitly whitelisted (no `*`)?
  - Are credentials properly restricted?
  - Are allowed methods limited to necessary HTTP verbs?

#### 7.2 Security Headers
- **Header Middleware:** Check security headers configuration
  - Is `X-Frame-Options` set to prevent clickjacking?
  - Is `X-Content-Type-Options: nosniff` enabled?
  - Is `Strict-Transport-Security` (HSTS) configured?
  - Is `Content-Security-Policy` defined?
  - Is `X-XSS-Protection` enabled?
  - Review `secure_headers` configuration in `main.py`

#### 7.3 SSRF Prevention
- **HTTP Client Whitelisting:** Review `apps/backend/src/http_client.py`
  - Is the `SafeAsyncClient` enforcing domain whitelist?
  - Are internal IPs (127.0.0.1, 169.254.169.254, 10.0.0.0/8) blocked?
  - Are redirects properly validated?

- **Frontend HTTP Client:** Review `apps/frontend/src/lib/axios.ts`
  - Are API endpoints whitelisted?
  - Is there protection against unauthorized external requests?

#### 7.4 API Documentation Exposure
- **Swagger/OpenAPI:** Check `main.py` lines 69-78
  - Are API docs disabled in production?
  - Is OpenAPI schema endpoint disabled in production?
  - Are internal endpoints hidden from documentation?

---

## 8. Frontend Security

**Focus Areas:** `apps/frontend/src/`

### Critical Security Checks:

#### 8.1 Authentication State Management
- **Auth Context/Store:** Review authentication state handling
  - Are tokens securely stored (httpOnly cookies preferred over localStorage)?
  - Are tokens cleared on logout?
  - Is there protection against XSS stealing tokens?

#### 8.2 Sensitive Data Handling
- **Client-Side PHI:** Check for PHI exposure
  - Is PHI stored in localStorage, sessionStorage, or IndexedDB?
  - Are console.log statements removed from production builds?
  - Is Redux DevTools disabled in production?

#### 8.3 Type Safety
- **TypeScript Configuration:** Review `docs/hardening/types.md` findings
  - Are all explicit `: any` types eliminated?
  - Are form schemas using generated types from `api-schemas.ts`?
  - Is error handling properly typed?

---

## 9. Dependencies & Supply Chain Security

### Critical Security Checks:

#### 9.1 Backend Dependencies
- **Python Packages:** Review `apps/backend/pyproject.toml` and `uv.lock`
  - Are all packages from trusted sources?
  - Are versions pinned to specific releases?
  - Are there known vulnerabilities (run `pip-audit` or `safety check`)?
  - Are dependencies minimized?

#### 9.2 Frontend Dependencies
- **NPM Packages:** Review `apps/frontend/package.json` and `pnpm-lock.yaml`
  - Are all packages from npm registry?
  - Are versions pinned?
  - Are there known vulnerabilities (run `pnpm audit`)?
  - Are unused dependencies removed?

#### 9.3 Pre-commit Hooks
- **Security Checks:** Review `.pre-commit-config.yaml`
  - Are secret scanning tools enabled?
  - Are security linters configured?
  - Is Checkov enabled for IaC scanning?

---

## 10. Testing & Code Quality

### Critical Security Checks:

#### 10.1 Test Security
- **Test Data:** Review test files
  - Are production credentials NEVER used in tests?
  - Is test data properly sanitized?
  - Are mocked services secure?

#### 10.2 Code Coverage
- **Security-Critical Paths:** Verify test coverage
  - Are authentication flows tested?
  - Are authorization checks tested?
  - Are RLS policies tested?
  - Are audit logging tested?

---

## Output Deliverable Format

Provide a comprehensive **Markdown Security Report** with the following structure:

### Executive Summary
- **Overall Security Posture:** Grade (A-F) with justification
- **Critical Findings Count:** P0, P1, P2 breakdown
- **Compliance Status:** HIPAA compliance assessment
- **Recommended Priority Actions:** Top 3-5 immediate fixes

### Vulnerability Findings

For each finding, provide:

| Severity | Category | Location | Description | Impact | Remediation |
|----------|----------|----------|-------------|--------|-------------|
| P0/P1/P2 | Auth/IDOR/etc | `file:line` | Technical description | Business impact | Specific fix |

**Severity Levels:**
- **P0 (Critical):** Immediate PHI exposure, tenant isolation bypass, authentication bypass
- **P1 (High):** Major compliance gaps, privilege escalation, significant data leak
- **P2 (Medium):** Security enhancements, defense-in-depth improvements
- **P3 (Low):** Best practices, code quality improvements

**Categories:**
- Authentication Bypass
- Authorization Failure (IDOR)
- Information Disclosure
- Injection (SQL, XSS, etc.)
- Cryptographic Failure
- Security Misconfiguration
- Vulnerable Dependencies
- Business Logic Flaw
- Compliance Violation

### Positive Findings
Document security controls that are correctly implemented:
- Well-designed RLS implementation
- Proper audit logging
- Good secret management
- etc.

### Recommendations
Prioritized list of improvements:
1. **Immediate (P0):** Fix within 24 hours
2. **Short-term (P1):** Fix within 1 week
3. **Medium-term (P2):** Fix within 1 month
4. **Long-term (P3):** Continuous improvement

### Compliance Checklist
HIPAA compliance assessment:
- [ ] Access Controls
- [ ] Audit Controls
- [ ] Integrity Controls
- [ ] Transmission Security
- [ ] etc.

---

## Methodology & Approach

1. **Start with Critical Paths:**
   - Begin with authentication (`apps/backend/src/security/auth.py`)
   - Then database session security (`apps/backend/src/database.py`)
   - Then authorization and RLS
   - Then audit logging

2. **Use Tools:**
   - **Grep** for dangerous patterns: `: any`, `text()`, `dangerouslySetInnerHTML`, `print(`, `console.log`
   - **Glob** for finding files by type
   - **Read** critical files completely
   - **Bash** for running security scanners if available

3. **Be Thorough but Practical:**
   - Focus on HIGH and CRITICAL severity issues first
   - Provide specific, actionable remediation steps
   - Include code examples where helpful
   - Reference industry standards (OWASP, NIST, HIPAA)

4. **Think Like an Attacker:**
   - How would you bypass authentication?
   - How would you access another tenant's data?
   - How would you extract PHI?
   - How would you escalate privileges?

---

## Key Files to Review (Priority Order)

### Critical Security Files:
1. `apps/backend/src/security/auth.py` - Authentication
2. `apps/backend/src/database.py` - RLS and session management
3. `apps/backend/src/middleware/audit.py` - Audit logging
4. `apps/backend/src/security/org_access.py` - Multi-tenancy
5. `apps/backend/src/logging.py` - PHI masking
6. `apps/backend/src/config.py` - Configuration and secrets
7. `apps/backend/src/main.py` - Application setup and middleware

### Data Model & Migrations:
8. `apps/backend/migrations/versions/f47bf61a922e_audit_and_rls.py` - RLS policies
9. `apps/backend/src/models/` - All model definitions
10. `docs/requirements/04 - sql.ddl` - Database schema

### API Endpoints (all files in):
11. `apps/backend/src/api/*.py` - All API routes

### Frontend Security:
12. `apps/frontend/src/components/auth-guard.tsx` - Route protection
13. `apps/frontend/src/lib/axios.ts` - HTTP client
14. `apps/frontend/src/hooks/api/*.ts` - API integration

### Infrastructure:
15. `infra/aws/*.tf` - Cloud infrastructure
16. `docker-compose.yml` - Container orchestration
17. `.github/workflows/*.yml` - CI/CD pipelines

---

## Additional Context

**Project Documentation:**
- Architecture: `docs/architecture/SETUP.md`
- Tech Stack: `docs/tech-stack/00 - Overview.md`
- API Reference: `docs/requirements/05 - API Reference.md`
- Type Hardening: `docs/hardening/types.md`
- Previous Reviews: `docs/review/`

**Key Technologies:**
- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Pydantic v2, Firebase Admin SDK, Presidio
- **Frontend:** TypeScript, React, Vite, TanStack Router/Query, Zod, shadcn/ui
- **Database:** PostgreSQL 15+ with RLS
- **Cache:** Redis 7
- **Infrastructure:** OpenTofu, AWS (S3, SES, Route53), Aptible
- **Security:** SlowAPI (rate limiting), Sentry (monitoring), SOPS (secrets)

**Compliance Requirements:**
- HIPAA compliant (PHI handling)
- Multi-tenant isolation (healthcare organizations)
- Audit logging (6+ year retention)
- MFA for staff
- Encryption at rest and in transit

---

## Start Your Audit

Begin by analyzing the authentication and authorization layer, then systematically work through each section above. Use the tools available to you (Grep, Glob, Read, Bash) to thoroughly examine the codebase.

**First Steps:**
1. Read and analyze `apps/backend/src/security/auth.py`
2. Read and analyze `apps/backend/src/database.py`
3. Check RLS implementation in migrations
4. Audit API endpoints for IDOR vulnerabilities
5. Review audit logging implementation
6. Check for PHI leakage in logging
7. Examine infrastructure security
8. Review frontend security controls

Good luck with your audit! Be thorough, be specific, and prioritize findings based on actual risk to patient data and system integrity.
