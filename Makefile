.PHONY: dev build test lint clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

dev: ## Run local development environment
	@echo "Starting local development environment..."
	# We will likely delegate to docker-compose here later
	@echo "Run 'docker compose up' (once configured)"

build: ## Build the project
	@echo "Building project..."
	cd frontend && pnpm build

test: ## Run tests
	@echo "Running tests..."
	cd backend && uv run pytest
	cd frontend && pnpm test

lint: ## Run linters
	@echo "Running linters..."
	cd backend && uv run ruff check .
	cd backend && uv run mypy .
	cd frontend && pnpm lint

clean: ## Clean up build artifacts
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
