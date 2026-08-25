# AI Agent Hub - Quick Start Guide

## 📋 Overview

This document provides a quick reference for setting up the AI Agent Hub project.

## ⚡ Quick Setup (Copy-Paste Friendly)

### All-in-One Setup Script

Save this as `setup.sh` and run `bash setup.sh`:

```bash
#!/bin/bash
set -e

PROJECT_DIR="/Users/chandesh/work/code/playground/ai-agent-hub"
cd /Users/chandesh/work/code/playground

# Step 1: Create and initialize project
mkdir -p ai-agent-hub
cd ai-agent-hub

git init
git config user.email "dev@aiagent-hub.local"
git config user.name "AI Agent Hub Dev"

# Step 2: Create directories
mkdir -p backend/{app/{models,schemas,api,services,core,db},tests,migrations}
mkdir -p frontend
mkdir -p docs
mkdir -p scripts

# Step 3: Setup Backend
cd backend

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip setuptools wheel

cat > requirements.txt << 'REQEOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
PyJWT==2.8.1
bcrypt==4.1.0
pydantic==2.5.0
pydantic-settings==2.1.0
fastapi-cors==0.0.6
slowapi==0.1.9
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.1
black==23.12.0
flake8==6.1.0
mypy==1.7.1
isort==5.13.2
uvloop==0.19.0
REQEOF

pip install -r requirements.txt

# Create backend files (see SETUP_COMMANDS.md for detailed file contents)

cd ..

# Step 4: Setup Frontend
npm install -g @angular/cli@latest
ng new frontend --routing --style=css --skip-git=true
cd frontend
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
cd ..

echo "✅ Setup complete! See SETUP_COMMANDS.md for detailed steps."
```

## 📁 Project Structure

```
ai-agent-hub/
├── backend/                  # FastAPI backend
│   ├── .venv/               # Python virtual environment
│   ├── app/                 # Application code
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration, security
│   │   ├── db/             # Database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── tests/              # Unit and integration tests
│   ├── migrations/         # Alembic migrations
│   ├── requirements.txt    # Python dependencies
│   ├── .env                # Environment variables (git ignored)
│   └── Dockerfile          # Container definition
│
├── frontend/               # Angular + TailwindCSS
│   ├── src/               # Source code
│   ├── node_modules/      # npm dependencies (git ignored)
│   ├── angular.json       # Angular configuration
│   ├── package.json       # npm dependencies
│   ├── tailwind.config.js # TailwindCSS configuration
│   └── Dockerfile.dev     # Development container
│
├── docs/
│   └── requirements.md    # Full specifications & requirements
│
├── scripts/               # Utility scripts
├── docker-compose.yml     # Multi-service orchestration
├── .gitignore            # Git ignore rules
└── README.md             # Project overview
```

## 🚀 Development Workflow

### Option 1: Local Development (No Docker)

```bash
# Terminal 1: Backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Database (if using local PostgreSQL)
postgres -D /usr/local/var/postgres

# Terminal 3: Frontend
cd frontend
ng serve --port 4200
```

### Option 2: Docker Development

```bash
# Start all services
docker-compose up

# Services available at:
# - Backend: http://localhost:8000
# - Backend Docs: http://localhost:8000/docs
# - Frontend: http://localhost:4200
# - Database: localhost:5432
```

## 🔧 Common Commands

### Backend

```bash
cd backend
source .venv/bin/activate

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Format code
black .

# Lint
flake8 .

# Type checking
mypy .

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "Add new table"
```

### Frontend

```bash
cd frontend

# Development server
ng serve

# Build for production
ng build --configuration production

# Run tests
ng test

# Run linter
ng lint

# Generate component
ng generate component components/my-component

# Generate service
ng generate service services/my-service
```

## 📝 Key Files to Customize

1. **Backend Configuration**: `backend/app/core/config.py`
2. **Database Connection**: `backend/.env`
3. **Frontend Environment**: `frontend/src/environments/`
4. **Project Requirements**: `docs/requirements.md`

## 🗄️ Database

### PostgreSQL Connection String

Development (Docker):
```
postgresql://postgres:postgres@db:5432/ai_agent_hub
```

Local:
```
postgresql://postgres:postgres@localhost:5432/ai_agent_hub
```

### Create Database Locally

```bash
createdb ai_agent_hub
```

## 📚 API Documentation

Once backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@host:5432/db
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:4200
```

### Frontend (environment.ts)

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1'
};
```

## 🧪 Testing

### Backend

```bash
# All tests
pytest

# Specific test file
pytest tests/test_health.py

# With coverage
pytest --cov=app --cov-report=html

# Watch mode
pytest-watch
```

### Frontend

```bash
# Run tests
ng test

# With coverage
ng test --code-coverage
```

## 📦 Dependencies Management

### Backend

```bash
# Add new dependency
pip install package-name
pip freeze > requirements.txt

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Frontend

```bash
# Add new dependency
npm install package-name

# Update dependencies
npm update

# Audit vulnerabilities
npm audit
npm audit fix
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Frontend won't compile
```bash
# Clear Angular cache
rm -rf .angular/cache

# Reinstall dependencies
rm -rf node_modules
npm install
```

### Database connection issues
```bash
# Check PostgreSQL is running
psql -U postgres -d template1 -c "SELECT version();"

# Check Docker network (if using Docker)
docker network inspect ai-agent-hub_app-network
```

## 📖 Documentation

- **Full Requirements**: See `docs/requirements.md`
- **Detailed Setup**: See `SETUP_COMMANDS.md`
- **Backend README**: `backend/README.md`
- **Frontend README**: `frontend/README.md`

## 🚢 Deployment (Future)

See deployment guides in `docs/` folder when ready to deploy to:
- Docker Compose (staging)
- Railway (recommended)
- AWS (scalable)

## 📊 Project Stats

- **Backend Framework**: FastAPI
- **Frontend Framework**: Angular 17+
- **Database**: PostgreSQL 15+
- **Styling**: TailwindCSS 3+
- **Containerization**: Docker + Docker Compose
- **Target Users**: 10,000+ concurrent
- **API Response Time**: <500ms (P95)

## 🤝 Next Steps

1. Run full setup: `bash setup.sh`
2. Review `docs/requirements.md` for specifications
3. Start development servers
4. Create first API endpoints for agents listing
5. Build UI components for agent discovery
6. Implement database models and migrations

---

**Status**: ✅ Ready for Development
**Last Updated**: 2025-11-23
**Maintainer**: Your Team
