.PHONY: install-all dev dev-stop dev-logs dev-logs-worker check test clean migrate seed seed-e2e seed-patients stop agent agent-install

# Default ports
FRONTEND_PORT ?= 5173
BACKEND_PORT ?= 8000

install-all:
	@echo "Installing Backend..."
	cd apps/backend && uv sync
	@echo "Installing Frontend..."
	cd apps/frontend && pnpm install
	@echo "Installing Pre-commit..."
	cd apps/backend && uv run pre-commit install
	@echo "Installing Agent..."
	cd agent && uv venv && . .venv/bin/activate && uv pip install -r requirements.txt

# Stop any existing dev processes
stop:
	@echo "Stopping existing processes..."
	@# Kill any node processes on frontend ports
	@-lsof -ti :5173 | xargs kill -9 2>/dev/null || true
	@-lsof -ti :5174 | xargs kill -9 2>/dev/null || true
	@-lsof -ti :5175 | xargs kill -9 2>/dev/null || true
	@# Stop docker containers
	@docker compose down 2>/dev/null || true
	@echo "All dev processes stopped."

# Start full dev environment (stops existing first)
dev: stop
	@echo "============================================"
	@echo "Starting Development Environment"
	@echo "============================================"
	@echo ""
	@echo "Starting Backend Services (Docker)..."
	docker compose up -d db redis api worker --build
	@echo ""
	@echo "Waiting for backend to be ready..."
	@sleep 3
	@until curl -s http://localhost:$(BACKEND_PORT)/health > /dev/null 2>&1; do \
		echo "  Waiting for API..."; \
		sleep 2; \
	done
	@echo "  ✓ Backend is ready at http://localhost:$(BACKEND_PORT)"
	@echo ""
	@echo "Starting Frontend (Vite)..."
	@echo "  → Frontend will be available at http://localhost:$(FRONTEND_PORT)"
	@echo ""
	cd apps/frontend && pnpm dev

# Start dev without stopping (for manual control)
dev-start:
	@echo "Starting Backend (Docker)..."
	docker compose up -d db redis api worker --build
	@echo "Starting Frontend..."
	cd apps/frontend && pnpm dev

# Just stop dev processes (alias)
dev-stop: stop

# View backend logs
dev-logs:
	docker compose logs -f api

# View worker logs
dev-logs-worker:
	docker compose logs -f worker

# View all service logs
dev-logs-all:
	docker compose logs -f

migrate:
	@echo "Running Migrations..."
	docker compose exec api alembic upgrade head

# Database Seeding
seed: seed-e2e
	@echo "✓ Database seeded"

seed-e2e:
	@echo "Seeding E2E test data (users, organization, patient, staff, provider)..."
	docker compose exec api python scripts/seed_e2e.py

seed-patients:
	@echo "Seeding 50 dummy patients..."
	docker compose exec api python scripts/seed_patients.py

check:
	@echo "Running Checks..."
	@echo "Backend Ruff..."
	cd apps/backend && uv run ruff check .
	cd apps/backend && uv run ruff format --check .
	@echo "Frontend Biome..."
	cd apps/frontend && pnpm biome check .
	@echo "Pre-commit..."
	apps/backend/.venv/bin/pre-commit run --all-files

test:
	@echo "Running Tests..."
	@echo "Backend..."
	docker compose exec api python -m pytest
	@echo "Frontend..."
	cd apps/frontend && pnpm test

test-backend:
	docker compose exec api python -m pytest

test-frontend:
	cd apps/frontend && pnpm test

clean:
	@echo "Cleaning up..."
	rm -rf apps/backend/.venv apps/frontend/node_modules
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"

# Agent Commands
agent-install:
	@echo "Setting up Agent environment..."
	cd agent && uv venv && . .venv/bin/activate && uv pip install -r requirements.txt
	@echo "✓ Agent dependencies installed"

agent:
	@echo "Starting AI Agent..."
	cd agent && . .venv/bin/activate && python run.py

# Show help
help:
	@echo "Available commands:"
	@echo "  make install-all   - Install all dependencies"
	@echo "  make dev           - Stop existing & start full dev environment"
	@echo "  make stop          - Stop all dev processes"
	@echo "  make dev-logs      - View backend API logs"
	@echo "  make dev-logs-worker - View ARQ worker logs"
	@echo "  make migrate       - Run database migrations"
	@echo "  make seed          - Seed database with E2E test data"
	@echo "  make seed-e2e      - Seed E2E users (super admin, staff, provider, patient)"
	@echo "  make seed-patients - Seed 50 dummy patients"
	@echo "  make check         - Run linters"
	@echo "  make test          - Run all tests"
	@echo "  make test-backend  - Run backend tests only"
	@echo "  make test-frontend - Run frontend tests only"
	@echo "  make agent-install - Install agent dependencies"
	@echo "  make agent         - Run AI agent workflow"
	@echo "  make clean         - Remove generated files"

