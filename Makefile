.PHONY: install-all dev check test clean migrate

install-all:
	@echo "Installing Backend..."
	cd backend && uv sync
	@echo "Installing Frontend..."
	cd frontend && pnpm install
	@echo "Installing Pre-commit..."
	cd backend && uv run pre-commit install

dev:
	@echo "Starting Backend (Docker)..."
	docker compose up -d db redis api --build
	@echo "Backend is running. Logs: 'docker compose logs -f api'"
	@echo "Starting Frontend (Local)..."
	cd frontend && pnpm dev

migrate:
	@echo "Running Migrations (Pending Epic 2)..."
	# cd backend && uv run alembic upgrade head

check:
	@echo "Running Checks..."
	@echo "Backend Ruff..."
	cd backend && uv run ruff check .
	cd backend && uv run ruff format --check .
	@echo "Frontend Biome..."
	cd frontend && pnpm biome check .
	@echo "Pre-commit..."
	backend/.venv/bin/pre-commit run --all-files

test:
	@echo "Running Tests..."
	@echo "Backend..."
	# cd backend && uv run pytest
	@echo "Frontend..."
	# cd frontend && pnpm test

clean:
	rm -rf backend/.venv frontend/node_modules
	find . -type d -name "__pycache__" -exec rm -rf {} +
