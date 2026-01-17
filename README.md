# Lockdev SaaS Starter

A HIPAA-compliant, AI-native SaaS starter kit.

## Tech Stack
- **Backend:** Python 3.11 + FastAPI + UV + SQLAlchemy + PostgreSQL
- **Frontend:** React + Vite + TanStack + Tailwind + Shadcn/ui
- **Infrastructure:** Docker Compose (Local), AWS + Aptible (Production)
- **AI:** Google Vertex AI (Gemini)
- **Auth:** Firebase Authentication

## Quick Start

### 1. Prerequisites
- Docker & Docker Compose
- Node.js & pnpm
- Python 3.11 & uv

### 2. Setup
```bash
# Install dependencies
make install-all

# Setup env vars
cp .env.example .env
```

### 3. Run
```bash
# Start all services
make dev
```

Visit:
- Frontend: [http://localhost:5173](http://localhost:5173)
- API Docs: [http://localhost:8001/docs](http://localhost:8001/docs)
- Admin Panel: [http://localhost:8001/admin](http://localhost:8001/admin)

## Documentation
See the `docs/` directory for detailed documentation.
