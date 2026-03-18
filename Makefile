.DEFAULT_GOAL := help

.PHONY: help setup check-env dev test build clean seed lint format smoke dist

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Install dependencies and create .env files from templates
	@echo "==> Installing backend dependencies..."
	cd backend && pip install -r requirements-dev.txt
	@echo "==> Installing frontend dependencies..."
	cd frontend && pnpm install
	@echo "==> Creating .env files (will not overwrite existing)..."
	[ -f backend/.env ] || cp -n backend/.env.example backend/.env
	[ -f frontend/.env.local ] || cp -n frontend/.env.example frontend/.env.local
	@echo "==> Checking environment variables..."
	-@python3 scripts/check_env.py
	@echo "==> Running database migrations..."
	cd backend && alembic upgrade head
	@echo "==> Setup complete"

check-env: ## Validate environment variable configuration
	@python3 scripts/check_env.py

dev: ## Start backend, frontend, and monitoring stack
	@echo "Starting all services..."
	@echo "  Backend:    http://localhost:8000"
	@echo "  Frontend:   http://localhost:3000"
	@echo "  Grafana:    http://localhost:3001"
	@trap 'kill 0' EXIT; \
		cd backend && uvicorn app.main:app --reload --port 8000 & \
		cd frontend && pnpm dev & \
		cd monitoring && docker compose up -d && \
		wait

test: ## Run backend and frontend test suites
	@echo "==> Running backend tests..."
	cd backend && pytest --cov=app --cov-report=term-missing tests/
	@echo "==> Running frontend tests..."
	cd frontend && pnpm test

build: ## Build Docker images via docker-compose
	docker compose build

seed: ## Seed demo data into the database
	@echo "==> Seeding demo data..."
	cd backend && python -m scripts.seed
	@echo "==> Seed complete"

lint: ## Run linters on backend and frontend
	@echo "==> Running ruff on backend..."
	cd backend && ruff check app/ tests/
	@echo "==> Running ESLint on frontend..."
	cd frontend && pnpm lint

format: ## Format code
	@echo "==> Formatting backend..."
	cd backend && ruff format app/ tests/

smoke: ## Run smoke tests against a running API
	@./scripts/smoke_test.sh

clean: ## Stop services and remove build artifacts
	@echo "==> Stopping monitoring stack..."
	-cd monitoring && docker compose down
	@echo "==> Stopping root docker-compose..."
	-docker compose down
	@echo "==> Removing build artifacts..."
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/node_modules/.cache frontend/.next
	@echo "==> Clean complete"

dist: ## Create distributable zip for marketplace delivery
	@./scripts/dist.sh
