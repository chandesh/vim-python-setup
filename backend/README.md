# AI Agent Hub - Backend

FastAPI-based backend for AI Agent Hub platform.

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Python**: 3.11+
- **Package Manager**: uv
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0

## Database Users

This project follows security best practices by separating database users:

- **Admin User**: `postgres` (password: `postgres_admin_password`) - For database administration only
- **Application User**: `ai_agent_app` (password: `ai_agent_app_password`) - Used by the application with limited privileges

## Ports

- **Backend API**: 8333
- **PostgreSQL**: 5435 (host) → 5432 (container)

## Development with Docker

### Start all services
```bash
docker-compose up
```

### Start only database
```bash
docker-compose up db
```

### Backend logs
```bash
docker logs -f ai_agent_hub_backend
```

### Access PostgreSQL (admin)
```bash
docker exec -it ai_agent_hub_db psql -U postgres -d ai_agent_hub
```

### Access PostgreSQL (app user)
```bash
docker exec -it ai_agent_hub_db psql -U ai_agent_app -d ai_agent_hub
```

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8333/docs
- ReDoc: http://localhost:8333/redoc
- Health Check: http://localhost:8333/health

## Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Configuration, security
│   ├── db/            # Database connection
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── main.py        # FastAPI app
├── tests/             # Tests
├── migrations/        # Alembic migrations
├── pyproject.toml     # Dependencies (managed by uv)
├── Dockerfile         # Container definition
├── init-db.sql        # Database initialization
└── .env.example       # Environment template
```

## Database Migrations

```bash
# Create migration
docker exec -it ai_agent_hub_backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker exec -it ai_agent_hub_backend alembic upgrade head
```

## Testing

```bash
docker exec -it ai_agent_hub_backend pytest
```

## Environment Variables

See `.env.example` for all available configuration options.
