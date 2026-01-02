# Setup Guide

This guide covers provisioning all required cloud services for local development and production.

## Cloud Services Overview

| Service | Purpose | Provisioning Method | Environment |
|---------|---------|---------------------|-------------|
| PostgreSQL | Primary database | Docker Compose | Local |
| Redis | Cache & job queue | Docker Compose | Local |
| Firebase/GCIP | Authentication | **ClickOps** (Console) | All |
| Sentry | Error tracking | **ClickOps** (Console) | All |
| AWS S3 | Document storage | **OpenTofu** | Staging/Prod |
| AWS SES | Transactional email | **OpenTofu** | Staging/Prod |
| AWS Route53 | DNS | **OpenTofu** | Prod |
| AWS IAM | Service accounts | **OpenTofu** | All |
| Aptible | Container hosting | **ClickOps** (Dashboard) | Staging/Prod |

---

## ClickOps Services (Manual Console Setup)

### 1. Firebase / Google Cloud Identity Platform

**One-time setup via GCP Console**

1. Create project at [console.firebase.google.com](https://console.firebase.google.com)

2. Enable Authentication > Sign-in providers:
   - Email/Password
   - Google (optional)

3. Enable Multi-Factor Authentication for Staff users:
   - Authentication > Settings > Multi-factor authentication

4. Configure SMTP (AWS SES) for email delivery:
   - Settings > Email Templates > SMTP Settings
   - Use SES SMTP credentials from OpenTofu outputs

5. Download service account JSON:
   - Project Settings > Service Accounts > Generate New Private Key
   - Save as `service-account.json`

6. Copy values to `backend/.env`:
   ```bash
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
   FIREBASE_PROJECT_ID=your-project-id
   ```

7. Copy Firebase web config to `frontend/.env`:
   ```bash
   VITE_FIREBASE_API_KEY=...
   VITE_FIREBASE_AUTH_DOMAIN=...
   VITE_FIREBASE_PROJECT_ID=...
   ```

### 2. Sentry

**One-time setup via sentry.io**

1. Create project at [sentry.io](https://sentry.io)

2. Select "FastAPI" as platform

3. Copy DSN to `backend/.env`:
   ```bash
   SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
   ```

4. **HIPAA Note:** Disable "Send Default PII" in project settings:
   - Settings > General Settings > Data Privacy

### 3. Aptible

**One-time setup via Aptible Dashboard**

1. Create account at [aptible.com](https://aptible.com)

2. Create Environment (e.g., `lockdev-staging`)

3. Create Application:
   - Name: `lockdev-api`
   - Git Remote URL will be provided

4. Create Database:
   - Type: PostgreSQL 15
   - Name: `lockdev-db`

5. Create Redis instance:
   - Type: Redis 7
   - Name: `lockdev-redis`

6. Note the connection strings for environment variables

7. Configure Log Drain to CloudWatch:
   - Environment > Log Drains > Create Log Drain
   - Select "CloudWatch"
   - Use credentials from OpenTofu outputs

---

## OpenTofu Services (Infrastructure as Code)

These services are provisioned automatically via OpenTofu in `infra/aws/`.

### Prerequisites

1. Install OpenTofu:
   ```bash
   brew install opentofu  # macOS
   ```

2. Configure AWS credentials:
   ```bash
   aws configure
   # Or use environment variables:
   export AWS_ACCESS_KEY_ID=...
   export AWS_SECRET_ACCESS_KEY=...
   export AWS_REGION=us-west-2
   ```

### Bootstrap (One-Time)

Before running `tofu init`, create the state backend:

```bash
# Create S3 bucket for Terraform state
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

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name lockdev-tf-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-west-2
```

### Provision AWS Resources

```bash
cd infra/aws

# Initialize OpenTofu
tofu init

# Create terraform.tfvars
cat > terraform.tfvars << EOF
environment     = "staging"
domain_name     = "staging.lockdev.com"
aws_region      = "us-west-2"
enable_route53  = false  # Set to true if you own the domain
EOF

# Preview changes
tofu plan

# Apply changes
tofu apply
```

### What Gets Created

| Resource | Purpose |
|----------|---------|
| **S3 Bucket** | Document storage with versioning & encryption |
| **S3 Quarantine Bucket** | Virus-infected file quarantine |
| **SES Domain** | Verified domain for sending email |
| **SES SMTP User** | SMTP credentials for transactional email |
| **Route53 Zone** | DNS zone (if enabled) |
| **Secrets Manager** | GCP credentials, Stripe keys |
| **CloudWatch Log Groups** | Centralized logging |
| **Lambda - Virus Scan** | ClamAV-based file scanning |

### Retrieve Outputs

```bash
# Get all outputs
tofu output

# Get specific values
tofu output ses_smtp_username
tofu output -raw ses_smtp_password

# Get CloudWatch log drain credentials
tofu output cloudwatch_log_drain_access_key_id
tofu output -raw cloudwatch_log_drain_secret_key
```

---

## Local Development Credentials

For local development, you need:

| Credential | How to Get | Required |
|------------|------------|----------|
| Firebase Service Account | GCP Console > IAM > Service Accounts | Yes |
| AWS Access Keys | AWS Console > IAM > Users > Security Credentials | Optional* |
| Sentry DSN | Sentry Dashboard > Project Settings > Client Keys | Optional |
| Stripe Keys | Stripe Dashboard > Developers > API Keys | Optional |

*AWS credentials are only needed if testing document upload, email, or Textract locally.

### backend/.env Example

```bash
# Required
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/lockdev
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secure-secret-key-here

# Firebase (Required)
GOOGLE_CLOUD_PROJECT=your-firebase-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Optional - AWS
AWS_S3_BUCKET=lockdev-documents-staging
AWS_REGION=us-west-2

# Optional - Stripe
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Optional - Observability
SENTRY_DSN=https://...@sentry.io/...
```

### frontend/.env Example

```bash
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
```

---

## Environment-Specific Configuration

### Development
- Use Docker Compose for PostgreSQL and Redis
- Use local Firebase project or emulator
- Mock external services (AWS, Stripe)

### Staging
- Use Aptible for hosting
- Use full AWS infrastructure
- Use Stripe test mode

### Production
- Use Aptible with dedicated resources
- Enable Route53 for DNS
- Use Stripe live mode
- Enable full audit logging

---

## Verification Checklist

After setup, verify each service works:

- [ ] `docker compose up -d` starts PostgreSQL and Redis
- [ ] `uv run alembic upgrade head` runs migrations
- [ ] `uv run uvicorn src.main:app --reload` starts API
- [ ] http://localhost:8000/health returns `{"status": "ok"}`
- [ ] http://localhost:8000/docs loads Swagger UI
- [ ] Firebase authentication works in frontend
- [ ] (Optional) S3 upload URL generation works
- [ ] (Optional) Stripe checkout session creation works

---

## Troubleshooting

### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker compose ps db

# Check connection
docker compose exec db psql -U postgres -c "SELECT 1"
```

### Redis Connection Failed
```bash
# Check if Redis is running
docker compose ps redis

# Check connection
docker compose exec redis redis-cli ping
```

### Firebase Token Verification Failed
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to valid service account JSON
- Ensure the Firebase project ID matches

### AWS S3 Access Denied
- Check IAM user has correct policies
- Verify bucket name and region match configuration
