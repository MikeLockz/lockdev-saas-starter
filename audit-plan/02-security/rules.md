# Security Audit Rules

## Scope
- `backend/src/` — API, middleware, services
- `frontend/src/` — React application
- `.env.example`, `.sops.yaml` — Secrets config
- `.github/workflows/` — CI/CD pipelines

---

## Rules

### SEC-001: No Hardcoded Secrets
**Severity:** 🔴 P0  
**Requirement:** No API keys, passwords, or tokens in source code.  
**Check:**
```bash
# Check for common secret patterns
grep -rE "(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]" backend/ frontend/ --include="*.py" --include="*.ts" --include="*.tsx"
# Check for AWS keys
grep -rE "AKIA[0-9A-Z]{16}" .
# Check for private keys
grep -rE "BEGIN (RSA|PRIVATE|OPENSSH)" .
```
**Exclusions:** `.env.example` with placeholder values (e.g., `your-secret-here`)

---

### SEC-002: Domain Whitelisting (SSRF Protection)
**Severity:** 🔴 P0  
**Requirement:** All outbound HTTP requests must use domain whitelisting.  
**Backend Check:**
```bash
grep -r "ALLOWED_DOMAINS" backend/src/http_client.py
grep -r "validate_url" backend/src/http_client.py
```
**Frontend Check:**
```bash
grep -r "ALLOWED_DOMAINS" frontend/src/lib/axios.ts
```
**Expected:** Whitelist includes only: AWS services, Firebase/GCIP, and application domains.

---

### SEC-003: PII Masking in Logs
**Severity:** 🔴 P0  
**Requirement:** Presidio must be used for PII masking in exception tracebacks. Sensitive keys must be redacted in all logs.  
**Check:**
```bash
grep -r "presidio" backend/src/logging.py backend/src/main.py
grep -r "mask\|redact" backend/src/logging.py
```
**Additional:** Verify `send_default_pii=False` in Sentry config.
```bash
grep -r "send_default_pii" backend/src/main.py
```

---

### SEC-004: MFA Enforcement for Privileged Roles
**Severity:** 🔴 P0  
**Requirement:** MFA must be mandatory for STAFF, PROVIDER, and ADMIN roles.  
**Check:**
```bash
grep -r "mfa" backend/src/security/auth.py backend/src/middleware/
grep -r "MFA" backend/src/
```
**Expected:** Middleware or dependency checking MFA claims in JWT before granting Staff access.

---

### SEC-005: Security Headers (Helmet Equivalent)
**Severity:** 🟠 P1  
**Requirement:** Security headers must be set via `secure` package middleware.  
**Headers Required:** HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy  
**Check:**
```bash
grep -r "secure.Secure" backend/src/main.py
grep -r "SecurityHeadersMiddleware" backend/src/main.py
```

---

### SEC-006: Rate Limiting
**Severity:** 🟠 P1  
**Requirement:** Rate limiting must be configured on all API endpoints via SlowAPI.  
**Check:**
```bash
grep -r "Limiter" backend/src/main.py
grep -r "SlowAPIMiddleware" backend/src/main.py
grep -r "@limiter.limit" backend/src/api/
```
**Expected:** Default limit and specific limits on sensitive endpoints (login, password reset).

---

## General Best Practices

### SEC-007: Dependency Vulnerability Scanning
**Severity:** 🟠 P1  
**Requirement:** Dependencies must be scanned for known vulnerabilities in CI/CD.  
**Check:**
```bash
grep -r "safety\|pip-audit\|snyk\|dependabot" .github/workflows/
cat .github/dependabot.yml 2>/dev/null
```
**Tools:** `pip-audit` (Python), `pnpm audit` (Node), Dependabot/Snyk

---

### SEC-008: Error Information Leakage
**Severity:** 🟠 P1  
**Requirement:** Production errors must NOT expose stack traces, internal paths, or database details to clients.  
**Check:**
```bash
grep -r "debug=True\|DEBUG=True" backend/src/
grep -r "exc_info\|traceback" backend/src/api/
```
**Expected:** Custom exception handlers returning sanitized error messages.

---

### SEC-009: CSRF Protection
**Severity:** 🟠 P1  
**Requirement:** State-changing endpoints must be protected against CSRF attacks.  
**Check:**
```bash
grep -r "csrf\|CSRF\|SameSite" backend/src/
grep -r "withCredentials" frontend/src/
```
**Expected:** SameSite cookies or CSRF tokens for authenticated requests.

---

### SEC-010: Input Length Limits
**Severity:** 🟡 P2  
**Requirement:** All string inputs must have maximum length constraints to prevent DoS.  
**Check:**
```bash
grep -r "max_length\|MaxLen\|Field(.*max" backend/src/models/ backend/src/schemas/
```

---

### SEC-011: Secure Password Handling
**Severity:** 🔴 P0  
**Requirement:** Passwords must be hashed with bcrypt/argon2, never stored plaintext or reversibly encrypted.  
**Check:**
```bash
grep -r "bcrypt\|argon2\|passlib" backend/src/ backend/pyproject.toml
grep -r "password_hash\|hashed_password" backend/src/models/
```

---

### SEC-012: Session Management
**Severity:** 🟠 P1  
**Requirement:** Sessions must have expiration, idle timeout, and secure cookie flags.  
**Check:**
```bash
grep -r "session\|Session\|expires\|max_age" backend/src/
grep -r "httponly\|secure\|samesite" backend/src/
```
