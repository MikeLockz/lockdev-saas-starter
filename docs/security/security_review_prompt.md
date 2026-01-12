# Security Audit Review Prompt

**Role:** Act as a Senior Security Architect and HIPAA Compliance Officer with 20+ years of experience in securing multi-tenant healthcare SaaS platforms.

**Objective:** Perform a holistic security audit of the Lockdev codebase to identify vulnerabilities, compliance gaps, and architectural weaknesses.

---

## 1. Compliance & Data Privacy (HIPAA)
Review the codebase for adherence to HIPAA requirements:
- **PHI Handling:** Ensure Protected Health Information (PHI) is never logged, cached on the client (PWA 'NetworkOnly' policy), or hardcoded in tests.
- **Encryption:** Verify that data is encrypted at rest (S3, RDS) and in transit (SSL/TLS).
- **PII Masking:** Audit the `presidio` integration in `backend/src/logging.py`. Does it correctly scrub logs and tracebacks? Check if telemetry events (`/api/telemetry`) are sanitized.
- **Audit Logging:** Verify that all READ/WRITE operations on PHI tables (Patients, Appointments, Notes) trigger an `AuditLog` entry. Check the `AuditMiddleware` and PostgreSQL triggers.
- **Data Retention:** Verify soft-delete implementation for clinical records.

## 2. Multi-Tenancy & Isolation
Audit the tenant isolation strategy:
- **Row Level Security (RLS):** Inspect `backend/src/database.py` and Alembic migrations. Are RLS policies correctly applied to all tenant-scoped tables?
- **Session Safety:** Verify the "Compliance Sandwich" pattern for connection pools. Does `DISCARD ALL` run on pool check-in? Are session variables (`app.current_tenant_id`) scoped to local transactions?
- **Query Scoping:** Ensure every repository/service query explicitly filters by `organization_id` or relies on a proven automatic filtering mechanism.

## 3. Authentication & Authorization
Audit the identity and access management layer:
- **Firebase/GCIP Integration:** Verify JWT token verification in `backend/src/security/auth.py`. Are claims (`sub`, `email`, `act_as`) validated?
- **MFA Enforcement:** Check if MFA is strictly enforced for `STAFF`, `PROVIDER`, and `ADMIN` roles before they can access PHI-accessing routes.
- **Role-Based Access Control (RBAC):** Review the `AuthGuard` (frontend) and role dependencies (backend). Is the principle of least privilege followed?
- **Impersonation ("Break Glass"):** Audit the impersonation flow. Does it require a reason? Is it capped at 1 hour? Is the `impersonator_id` correctly captured in audit logs?

## 4. Network & Infrastructure
Review infrastructure-as-code and network security:
- **SSRF Prevention:** Inspect the domain whitelisting in `frontend/src/lib/axios.ts` and `backend/src/http_client.py` (`SafeAsyncClient`). Is the whitelist too broad?
- **OpenTofu/IaC:** Check `infra/aws/` for security misconfigurations (e.g., public S3 buckets, weak IAM policies). Ensure `Checkov` scans are active.
- **Security Headers:** Verify `TrustedHostMiddleware`, `CORSMiddleware`, and `SecurityHeadersMiddleware` configuration in `main.py`.
- **Secret Management:** Ensure no secrets are in version control. Check `.sops.yaml` and `.env.example`.

## 5. AI Security
Audit the integration with Google Vertex AI:
- **Zero Retention:** Confirm that the Vertex AI client is configured for zero data retention.
- **Sanitization Pipeline:** Review the pipeline that scrubs PII/PHI *before* sending data to the LLM. Is the re-hydration of data safe?

## 6. Business Logic & Resilience
Check for common software vulnerabilities:
- **Rate Limiting:** Verify `SlowAPI` implementation. Are auth and PHI endpoints sufficiently protected?
- **Concurrency:** Audit appointment booking for race conditions. Is a locking strategy (Advisory locks or `FOR UPDATE`) implemented?
- **Input Validation:** Ensure Pydantic v2 and Zod schemas strictly validate all inputs. Look for any use of `any` types (Ref: `docs/hardening/types.md`).
- **Session Management:** Verify the 15-minute idle timeout and concurrent session policy.

---

## Output Format
Provide the audit findings in a structured report:
1. **Critical Vulnerabilities (P0):** Immediate risks to data isolation or PHI exposure.
2. **Major Compliance Gaps (P1):** Deviations from HIPAA or documented security standards.
3. **Security Enhancements (P2):** Opportunities to strengthen the security posture.
4. **Logic & Architecture Flaws:** Weaknesses in state machines, concurrency, or RBAC.

**Files to Reference:**
- `docs/04 - sql.ddl`
- `docs/05 - API Reference.md`
- `docs/09d - Critical Logic Specs.md`
- `agent/config/project_rules.md`
