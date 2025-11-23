.PHONY: help init build up down start stop restart logs clean rebuild db-only backend-only frontend-only ps shell-backend shell-db test

# Default target
help:
	@echo "AI Agent Hub - Available Commands"
	@echo "=================================="
	@echo ""
	@echo "Initial Setup:"
	@echo "  make init            - Initialize project (first time setup)"
	@echo ""
	@echo "Starting & Stopping:"
	@echo "  make up              - Start all services (detached)"
	@echo "  make start           - Start all services (attached, with logs)"
	@echo "  make down            - Stop all services"
	@echo "  make stop            - Stop all services (alias for down)"
	@echo "  make restart         - Restart all services"
	@echo ""
	@echo "Building:"
	@echo "  make build           - Build all Docker images"
	@echo "  make rebuild         - Rebuild all images from scratch (no cache)"
	@echo ""
	@echo "Individual Services:"
	@echo "  make db-only         - Start only database"
	@echo "  make backend-only    - Start database and backend"
	@echo "  make frontend-only   - Start only frontend"
	@echo ""
	@echo "Logs & Status:"
	@echo "  make logs            - View logs from all services"
	@echo "  make logs-backend    - View backend logs"
	@echo "  make logs-db         - View database logs"
	@echo "  make logs-frontend   - View frontend logs"
	@echo "  make ps              - Show running containers"
	@echo ""
	@echo "Shell Access:"
	@echo "  make shell-backend   - Open shell in backend container"
	@echo "  make shell-db        - Open PostgreSQL shell (app user)"
	@echo "  make shell-db-admin  - Open PostgreSQL shell (admin user)"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate      - Run database migrations"
	@echo "  make db-create       - Create new migration"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run backend tests"
	@echo "  make test-cov        - Run tests with coverage"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           - Stop and remove containers, networks"
	@echo "  make clean-all       - Clean everything including volumes"
	@echo ""
	@echo "Health:"
	@echo "  make health          - Check service health"
	@echo ""

# Initialize project
init:
	@echo "Initializing AI Agent Hub project..."
	@echo ""
	@echo "Step 1: Checking prerequisites..."
	@command -v docker >/dev/null 2>&1 || { echo "[ERROR] Docker is required but not installed. Aborting."; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "[ERROR] Docker Compose is required but not installed. Aborting."; exit 1; }
	@echo "[OK] Docker and Docker Compose are installed"
	@echo ""
	@echo "Step 2: Creating .env file for backend..."
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "[OK] Created backend/.env from .env.example"; \
	else \
		echo "[WARN] backend/.env already exists, skipping"; \
	fi
	@echo ""
	@echo "Step 3: Building Docker images..."
	@docker-compose build
	@echo "[OK] Docker images built successfully"
	@echo ""
	@echo "Step 4: Starting services..."
	@docker-compose up -d
	@echo "[OK] Services started"
	@echo ""
	@echo "Step 5: Waiting for database to be ready..."
	@sleep 5
	@docker exec ai_agent_hub_db pg_isready -U postgres >/dev/null 2>&1 && echo "[OK] Database is ready" || echo "[WARN] Database might still be starting"
	@echo ""
	@echo "[OK] Initialization complete!"
	@echo ""
	@echo "Services are running at:"
	@echo "   - Backend API: http://localhost:8333"
	@echo "   - API Docs: http://localhost:8333/docs"
	@echo "   - Health Check: http://localhost:8333/health"
	@echo "   - Frontend: http://localhost:4200 (when ready)"
	@echo "   - PostgreSQL: localhost:5435"
	@echo ""
	@echo "Next steps:"
	@echo "   - Run 'make health' to check service status"
	@echo "   - Run 'make logs' to view service logs"
	@echo "   - Run 'make help' to see all available commands"
	@echo ""

# Build
build:
	@echo "Building Docker images..."
	docker-compose build

rebuild:
	@echo "Rebuilding Docker images (no cache)..."
	docker-compose build --no-cache

# Start/Stop
up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo ""
	@echo "Services started!"
	@echo "- Backend API: http://localhost:8333"
	@echo "- Backend Docs: http://localhost:8333/docs"
	@echo "- Frontend: http://localhost:4200"
	@echo "- PostgreSQL: localhost:5435"

start:
	@echo "Starting all services (with logs)..."
	docker-compose up

down:
	@echo "Stopping all services..."
	docker-compose down

stop: down

restart:
	@echo "Restarting all services..."
	docker-compose restart

# Individual services
db-only:
	@echo "Starting database only..."
	docker-compose up -d db
	@echo "PostgreSQL is running on port 5435"

backend-only:
	@echo "Starting database and backend..."
	docker-compose up -d db backend
	@echo ""
	@echo "Backend API: http://localhost:8333"
	@echo "Backend Docs: http://localhost:8333/docs"

frontend-only:
	@echo "Starting frontend only..."
	docker-compose up -d frontend
	@echo "Frontend: http://localhost:4200"

# Logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-db:
	docker-compose logs -f db

logs-frontend:
	docker-compose logs -f frontend

# Status
ps:
	docker-compose ps

# Shell access
shell-backend:
	docker exec -it ai_agent_hub_backend /bin/bash

shell-db:
	@echo "Connecting as application user (ai_agent_app)..."
	docker exec -it ai_agent_hub_db psql -U ai_agent_app -d ai_agent_hub

shell-db-admin:
	@echo "Connecting as admin user (postgres)..."
	docker exec -it ai_agent_hub_db psql -U postgres -d ai_agent_hub

# Database migrations
db-migrate:
	@echo "Running database migrations..."
	docker exec -it ai_agent_hub_backend alembic upgrade head

db-create:
	@echo "Creating new migration..."
	@read -p "Migration name: " name; \
	docker exec -it ai_agent_hub_backend alembic revision --autogenerate -m "$$name"

# Testing
test:
	@echo "Running tests..."
	docker exec -it ai_agent_hub_backend pytest

test-cov:
	@echo "Running tests with coverage..."
	docker exec -it ai_agent_hub_backend pytest --cov=app --cov-report=html

# Cleanup
clean:
	@echo "Cleaning up containers and networks..."
	docker-compose down
	@echo "Cleanup complete!"

clean-all:
	@echo "[WARNING] This will remove all data including database volumes!"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose down -v; \
		echo "All containers, networks, and volumes removed!"; \
	else \
		echo "Cancelled."; \
	fi

# Health check
health:
	@echo "Checking service health..."
	@echo ""
	@echo "Backend Health:"
	@curl -s http://localhost:8333/health | python3 -m json.tool || echo "[ERROR] Backend not responding"
	@echo ""
	@echo "Database:"
	@docker exec ai_agent_hub_db pg_isready -U postgres && echo "[OK] Database is healthy" || echo "[ERROR] Database not responding"
	@echo ""
	@echo "Containers:"
	@docker-compose ps
