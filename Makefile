.PHONY: dev build test lint check clean install-all migrate help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install-all: ## Install dependencies for backend and frontend
	@echo "Installing backend dependencies..."
	cd backend && uv sync
	@echo "Installing frontend dependencies..."
	cd frontend && pnpm install

dev: ## Run local development environment via docker-compose
	@echo "Starting local development environment..."
	docker compose up -d

migrate: ## Run database migrations
	@echo "Running migrations..."
	cd backend && uv run alembic upgrade head

seed-patients: ## Seed dummy patient data
	@echo "Seeding patients..."
	cd backend && uv run scripts/seed_patients.py

test: ## Run tests
	@echo "Running tests..."
	cd backend && uv run pytest
	cd frontend && pnpm test

lint: ## Run linters
	@echo "Running linters..."
	pre-commit run --all-files

check: lint test ## Run all checks (lint + test)

clean: ## Clean up build artifacts
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete