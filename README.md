# Lockdev SaaS Starter

HIPAA-compliant healthcare SaaS platform with multi-tenant architecture, built for modern healthcare organizations.

## 🏥 Overview

Lockdev is a production-ready starter template for building HIPAA-compliant healthcare applications. It provides:

- **Multi-tenant architecture** with organization-level isolation
- **HIPAA compliance** features including audit logging, consent management, and PHI masking
- **Three user roles**: Patient, Staff (with MFA), and Super Admin
- **Real-time updates** via Server-Sent Events (SSE)
- **Document processing** with OCR and virus scanning
- **Subscription billing** via Stripe

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, SQLAlchemy (Async), PostgreSQL 15, Redis 7, ARQ |
| **Frontend** | React 18, Vite, TanStack (Query + Router), Zustand |
| **Auth** | Firebase/GCIP with MFA enforcement for staff |
| **AI** | Google Vertex AI (Gemini) for document analysis |
| **Payments** | Stripe Subscriptions & Billing Portal |
| **Infra** | Aptible (Containers), AWS (S3, SES, Textract, CloudWatch) |
| **IaC** | OpenTofu for AWS resource provisioning |

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- [Node.js 20+](https://nodejs.org/) & [pnpm](https://pnpm.io/)
- [Python 3.11+](https://www.python.org/) & [uv](https://docs.astral.sh/uv/)

### 1. Clone and Install

```bash
git clone https://github.com/your-org/lockdev-saas-starter.git
cd lockdev-saas-starter

# Install all dependencies
make install-all
```

### 2. Configure Environment

```bash
# Copy environment templates
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend/.env.example apps/frontend/.env

# Edit with your credentials (see docs/SETUP.md for details)
```

### 3. Start Development

```bash
# Start database services
docker compose up -d db redis

# Run database migrations
cd apps/backend && uv run alembic upgrade head && cd ../..

# Start API and Frontend (in separate terminals)
make dev
```

### 4. Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |
| Admin Panel | http://localhost:8000/admin |

### 5. Seed Test Data

```bash
# Seed E2E test users (runs inside Docker - no config needed)
make seed

# Or seed individually:
make seed-e2e      # Creates organization, super admin, staff, provider, patient
make seed-patients # Adds 50 dummy patients
```

#### Dev Login Users

After seeding, use these mock users via the dev login buttons on the login page:

| User | Email | Role |
|------|-------|------|
| Super Admin | `e2e@example.com` | Platform-wide admin |
| Staff | `staff@example.com` | Organization staff member |
| Provider | `provider@example.com` | Licensed provider (NPI: 1234567890) |
| Patient | `patient@example.com` | Patient portal user |

> **Note:** Dev login buttons only appear when running in development mode (`pnpm dev`).

## 📁 Project Structure

```
lockdev-saas-starter/
├── apps/                    # Application packages
│   ├── backend/             # FastAPI application
│   │   ├── src/
│   │   │   ├── api/         # API routes (events, users, webhooks, etc.)
│   │   │   ├── models/      # SQLAlchemy models
│   │   │   ├── services/    # Business logic (AI, billing, documents)
│   │   │   └── middleware/  # Auth, audit, context middleware
│   │   ├── migrations/      # Alembic migrations
│   │   └── tests/           # pytest test suite
│   └── frontend/            # React SPA
│       ├── src/
│       │   ├── components/  # Reusable UI components
│       │   ├── hooks/       # Custom hooks (useAuth, useAnalytics)
│       │   ├── routes/      # Page components
│       │   └── stores/      # Zustand state stores
│       └── public/          # Static assets
├── packages/                # Shared packages (future)
├── infra/                   # Infrastructure as Code
│   └── aws/                # OpenTofu AWS configuration
├── docs/                    # Documentation
│   ├── architecture/        # C4 and D2 diagrams
│   └── implementation-plan/ # Story-based implementation tracking
└── docker-compose.yml       # Local development services
```

## 📖 Documentation

- [Setup Guide](docs/SETUP.md) - Cloud service provisioning
- [API Reference](docs/05%20-%20API%20Reference.md) - Complete endpoint documentation
- [Architecture](docs/architecture/) - C4 and D2 diagrams
- [Implementation Plan](docs/implementation-plan/) - Story-based development tracking

## 🔒 Security & Compliance

### HIPAA Features

- **Row-Level Security (RLS)**: Tenant isolation at database level
- **Audit Logging**: All data changes logged with actor and timestamp
- **PHI Masking**: Sensitive data masked in logs using Presidio NLP
- **Consent Management**: HIPAA consent tracking per user
- **MFA Enforcement**: Required for staff users via Firebase

### Security Practices

- JWT-based authentication with token verification
- Rate limiting on all API endpoints
- Input validation via Pydantic
- SQL injection prevention via parameterized queries
- XSS prevention with secure headers
- CORS configuration for allowed origins only

## 🧪 Testing

```bash
# Backend tests
cd apps/backend
uv run pytest

# Frontend tests
cd apps/frontend
pnpm test

# E2E tests (Playwright)
cd apps/frontend
pnpm test:e2e
```

## 🚢 Deployment

### Aptible (Recommended for HIPAA)

1. Configure Aptible resources (see [docs/SETUP.md](docs/SETUP.md))
2. Set environment variables via `aptible config:set`
3. Deploy via Git push:

```bash
git remote add aptible git@beta.aptible.com:lockdev-prod/lockdev-api.git
git push aptible main
```

### AWS Infrastructure

```bash
cd infra/aws
tofu init
tofu plan
tofu apply
```

## 📊 Observability

- **Error Tracking**: Sentry for exceptions and APM
- **Logging**: Structured JSON logs via structlog → CloudWatch
- **Analytics**: Custom telemetry endpoint for behavioral tracking
- **Real-time**: SSE for instant user feedback

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ for healthcare innovation
