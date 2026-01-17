# Infrastructure Audit Rules

## Scope
- `infra/aws/` — OpenTofu/Terraform configurations
- `.github/workflows/` — CI/CD pipelines
- `.sops.yaml` — Secrets encryption config
- `docker-compose.yml` — Local development

---

## Rules

### INFRA-001: S3 Encryption and ACLs
**Severity:** 🔴 P0  
**Requirement:** All S3 buckets must have encryption enabled and private ACLs.  
**Check:**
```bash
grep -r "server_side_encryption_configuration\|encrypt" infra/aws/
grep -r "acl.*private\|block_public" infra/aws/
```
**Expected:** AES256 or KMS encryption, `block_public_acls = true`

---

### INFRA-002: Secrets Management
**Severity:** 🔴 P0  
**Requirement:** Production secrets must be stored in AWS Secrets Manager, not in environment files or code.  
**Check:**
```bash
grep -r "aws_secretsmanager_secret" infra/aws/
cat .sops.yaml  # Verify SOPS is configured for local dev
```
**Anti-Pattern Check:**
```bash
# Should NOT find real secrets in these files
grep -rE "^[A-Z_]+=[^$]" .env 2>/dev/null || echo "No .env file (good)"
```

---

### INFRA-003: Terraform State Security
**Severity:** 🟠 P1  
**Requirement:** Terraform state must use remote backend (S3) with encryption and DynamoDB locking.  
**Check:**
```bash
grep -r 'backend "s3"' infra/
grep -r "dynamodb_table\|encrypt.*true" infra/
```
**Expected:** S3 backend with encryption and lock table configured.

---

### INFRA-004: CI/CD Secrets Handling
**Severity:** 🔴 P0  
**Requirement:** GitHub Actions must not log secrets. Secrets must use `${{ secrets.* }}` syntax.  
**Check:**
```bash
grep -r "echo.*SECRET\|echo.*PASSWORD\|echo.*API_KEY" .github/workflows/
```
**Expected:** No matches. Secrets should never be echoed.

---

### INFRA-005: Virus Scanning on Uploads
**Severity:** 🟠 P1  
**Requirement:** S3 document uploads must trigger virus scanning (Lambda + ClamAV).  
**Check:**
```bash
grep -r "virus\|clamav\|scan" infra/aws/
grep -r "s3:ObjectCreated" infra/aws/
```
**Expected:** Lambda function triggered on S3 uploads, quarantine bucket for infected files.

---

## General Best Practices

### INFRA-006: Health Check Endpoints
**Severity:** 🟠 P1  
**Requirement:** Services must expose `/health` (shallow) and `/health/deep` (dependencies) endpoints.  
**Check:**
```bash
grep -r "/health" backend/src/main.py
grep -r "health" docker-compose.yml Procfile
```
**Expected:** Both shallow (web server up) and deep (DB/Redis connected) checks.

---

### INFRA-007: Graceful Shutdown
**Severity:** 🟠 P1  
**Requirement:** Services must handle SIGTERM gracefully, completing in-flight requests.  
**Check:**
```bash
grep -r "SIGTERM\|signal\|shutdown\|lifespan" backend/src/main.py
grep -r "on_shutdown" backend/src/
```

---

### INFRA-008: Resource Limits
**Severity:** 🟡 P2  
**Requirement:** Containers must have CPU/memory limits to prevent noisy neighbor issues.  
**Check:**
```bash
grep -r "memory\|cpu\|resources\|limits" docker-compose.yml
grep -r "container_size\|memory_limit" infra/
```

---

### INFRA-009: Dependency Pinning
**Severity:** 🟠 P1  
**Requirement:** All dependencies must be pinned to exact versions for reproducible builds.  
**Check:**
```bash
cat backend/uv.lock frontend/pnpm-lock.yaml infra/.terraform.lock.hcl 2>/dev/null | head -20
grep -r "==" backend/pyproject.toml
```
**Expected:** Lock files committed to repository.

---

### INFRA-010: Environment Parity
**Severity:** 🟡 P2  
**Requirement:** Development, staging, and production environments must use same base images and versions.  
**Check:**
```bash
grep -r "FROM\|image:" backend/Dockerfile docker-compose.yml
```
**Expected:** Explicit version tags (e.g., `python:3.11-slim`), not `latest`.

---

### INFRA-011: Log Retention
**Severity:** 🟡 P2  
**Requirement:** Logs must have defined retention periods (min 90 days for compliance).  
**Check:**
```bash
grep -r "retention\|log_group" infra/aws/
```
