# BillFusion Auth Service Makefile

.PHONY: help build up down logs shell test lint format clean migrate

# Default target
help:
	@echo "BillFusion Auth Service Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make build     - Build Docker images"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make logs      - Show logs"
	@echo "  make shell     - Open shell in auth service container"
	@echo ""
	@echo "Database:"
	@echo "  make migrate   - Run database migrations"
	@echo "  make db-shell  - Open database shell"
	@echo "  make db-reset  - Reset database (DESTRUCTIVE)"
	@echo ""
	@echo "Testing:"
	@echo "  make test      - Run tests"
	@echo "  make test-cov  - Run tests with coverage"
	@echo "  make lint      - Run linting"
	@echo "  make format    - Format code"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean     - Clean up containers and volumes"
	@echo "  make backup    - Backup database"
	@echo "  make restore   - Restore database from backup"

# Development commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started. Access:"
	@echo "  Auth Service: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo "  Grafana: http://localhost:3000 (admin/admin123)"
	@echo "  Prometheus: http://localhost:9090"

down:
	docker-compose down

logs:
	docker-compose logs -f auth-service

logs-all:
	docker-compose logs -f

shell:
	docker-compose exec auth-service /bin/bash

# Database commands
migrate:
	docker-compose exec auth-service alembic upgrade head

migrate-new:
	@read -p "Enter migration description: " desc; \
	docker-compose exec auth-service alembic revision --autogenerate -m "$$desc"

db-shell:
	docker-compose exec postgres psql -U postgres -d billfusion_auth

db-reset:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose down -v; \
		docker-compose up -d postgres redis; \
		sleep 10; \
		docker-compose exec auth-service alembic upgrade head; \
	fi

# Testing commands
test:
	docker-compose exec auth-service pytest

test-cov:
	docker-compose exec auth-service pytest --cov=app --cov-report=html --cov-report=term

test-local:
	pytest

lint:
	docker-compose exec auth-service flake8 app tests
	docker-compose exec auth-service mypy app

format:
	docker-compose exec auth-service black app tests
	docker-compose exec auth-service isort app tests

format-local:
	black app tests
	isort app tests

# Maintenance commands
clean:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

backup:
	@mkdir -p backups
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	docker-compose exec -T postgres pg_dump -U postgres billfusion_auth > backups/backup_$$timestamp.sql; \
	echo "Backup created: backups/backup_$$timestamp.sql"

restore:
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Usage: make restore BACKUP_FILE=backups/backup_20231201_120000.sql"; \
		exit 1; \
	fi
	@echo "WARNING: This will overwrite the current database!"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose exec -T postgres psql -U postgres -c "DROP DATABASE IF EXISTS billfusion_auth;"; \
		docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE billfusion_auth;"; \
		docker-compose exec -T postgres psql -U postgres billfusion_auth < $(BACKUP_FILE); \
		echo "Database restored from $(BACKUP_FILE)"; \
	fi

# Production commands
deploy-staging:
	@echo "Deploying to staging..."
	docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build

deploy-prod:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Development setup
setup-dev:
	@echo "Setting up development environment..."
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source venv/bin/activate  # Linux/Mac"
	@echo "  venv\\Scripts\\activate     # Windows"
	@echo "Then install dependencies with: pip install -r requirements.txt"

# Health checks
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "Auth service is not responding"
	@curl -f http://localhost:9090/-/healthy || echo "Prometheus is not responding"
	@curl -f http://localhost:3000/api/health || echo "Grafana is not responding"

# Monitoring
monitor:
	@echo "Opening monitoring dashboards..."
	@echo "Grafana: http://localhost:3000"
	@echo "Prometheus: http://localhost:9090"
	@echo "Auth Service Metrics: http://localhost:8000/metrics"

# Security checks
security-scan:
	@echo "Running security scans..."
	docker run --rm -v $$(pwd):/app -w /app python:3.11-slim pip install safety && safety check -r requirements.txt
	docker run --rm -v $$(pwd):/app -w /app python:3.11-slim pip install bandit && bandit -r app/

# Documentation
docs:
	@echo "Starting documentation server..."
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "ReDoc: http://localhost:8000/redoc"

# Install pre-commit hooks
install-hooks:
	pre-commit install

# Run pre-commit on all files
check-all:
	pre-commit run --all-files
