.PHONY: help install dev up down logs clean test lint format

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Done!"

dev: ## Start development environment with Docker Compose
	docker-compose up -d

up: dev ## Alias for dev

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

clean: ## Clean up containers, volumes, and build artifacts
	docker-compose down -v
	rm -rf frontend/node_modules frontend/.next
	rm -rf backend/__pycache__ backend/.pytest_cache backend/htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test: ## Run all tests
	@echo "Running frontend tests..."
	cd frontend && npm test
	@echo "Running backend tests..."
	cd backend && pytest

test-frontend: ## Run frontend tests only
	cd frontend && npm test

test-backend: ## Run backend tests only
	cd backend && pytest

lint: ## Run linters
	@echo "Linting frontend..."
	cd frontend && npm run lint
	@echo "Linting backend..."
	cd backend && flake8 && mypy app

format: ## Format code
	@echo "Formatting frontend..."
	cd frontend && npx prettier --write .
	@echo "Formatting backend..."
	cd backend && black . && isort .

setup-env: ## Create .env files from examples
	cp frontend/.env.local.example frontend/.env.local
	cp backend/.env.example backend/.env
	@echo "Environment files created. Please edit them with your configuration."

db-migrate: ## Run database migrations
	@echo "Running database migrations..."
	docker-compose exec postgres psql -U postgres -d ai_gym_coach -f /docker-entrypoint-initdb.d/001_create_schema.sql
	@echo "Migration completed!"

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "WARNING: This will destroy all data in the database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS ai_gym_coach;"; \
		docker-compose exec postgres psql -U postgres -c "CREATE DATABASE ai_gym_coach;"; \
		docker-compose exec postgres psql -U postgres -d ai_gym_coach -f /docker-entrypoint-initdb.d/001_create_schema.sql; \
		echo "Database reset completed!"; \
	fi

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d ai_gym_coach

db-status: ## Check database status and list tables
	@echo "Database status:"
	@docker-compose exec postgres psql -U postgres -d ai_gym_coach -c "\dt"

db-validate: ## Validate database schema
	@echo "Validating database schema..."
	@docker-compose exec postgres psql -U postgres -d ai_gym_coach -f /docker-entrypoint-initdb.d/validate_schema.sql

db-backup: ## Create database backup
	@echo "Creating database backup..."
	@docker-compose exec postgres pg_dump -U postgres ai_gym_coach > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup created: backup_$$(date +%Y%m%d_%H%M%S).sql"


