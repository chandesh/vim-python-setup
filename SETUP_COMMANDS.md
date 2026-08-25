# AI Agent Hub - Project Setup Commands

Execute these commands sequentially to set up the entire project structure, backend, frontend, and documentation.

## Step 1: Create Project Directory and Initialize Git

```bash
# Navigate to playground directory
cd path/to/your/workspace

# Create project directory
mkdir -p ai-agent-hub
cd ai-agent-hub

# Initialize Git repository
git init
git config user.email "you@example.com"
git config user.name "Your Name"

# Create basic .gitignore
cat > .gitignore << 'EOF'
# Backend
backend/.venv/
backend/__pycache__/
backend/*.pyc
backend/.pytest_cache/
backend/.coverage
backend/htmlcov/
backend/.env
backend/.env.local
backend/dist/
backend/build/
backend/*.egg-info/

# Frontend
frontend/node_modules/
frontend/dist/
frontend/.angular/
frontend/*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# OS
Thumbs.db
.DS_Store

# Docker
.env.docker
EOF

# Create basic README
cat > README.md << 'EOF'
# AI Agent Hub

A comprehensive platform for discovering and comparing AI agents and MCP servers.

## Project Structure

```
ai-agent-hub/
├── backend/              # FastAPI application
├── frontend/             # Angular application
├── docs/                 # Documentation
└── docker-compose.yml    # Local development setup
```

## Development

See individual README files in `backend/` and `frontend/` directories.

## Documentation

See `docs/requirements.md` for detailed project requirements and specifications.
EOF

git add .
git commit -m "Initial commit: Project scaffold"
```

## Step 2: Create Directory Structure

```bash
# Create main directories
mkdir -p backend
mkdir -p frontend
mkdir -p docs
mkdir -p scripts

# Backend subdirectories
mkdir -p backend/app/{models,schemas,api,services,core,db}
mkdir -p backend/tests
mkdir -p backend/migrations

# Frontend subdirectories will be created by Angular CLI

echo "Directory structure created successfully"
```

## Step 3: Setup Backend (FastAPI)

```bash
cd backend

# Create Python virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
PyJWT==2.8.1
bcrypt==4.1.0

# Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# CORS
fastapi-cors==0.0.6

# Rate Limiting
slowapi==0.1.9

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.1

# Code Quality
black==23.12.0
flake8==6.1.0
mypy==1.7.1
isort==5.13.2

# Development
uvloop==0.19.0
EOF

# Install dependencies
pip install -r requirements.txt

# Create .env template
cat > .env.example << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/ai_agent_hub

# Environment
ENVIRONMENT=development
DEBUG=true

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:4200,http://localhost:3000

# API
API_TITLE=AI Agent Hub API
API_VERSION=0.1.0

# OAuth (future)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EOF

cp .env.example .env

# Create app/__init__.py
touch app/__init__.py

# Create app/core/config.py
cat > app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    api_title: str = "AI Agent Hub API"
    api_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ai_agent_hub"
    
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    cors_origins: List[str] = ["http://localhost:4200", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF

# Create app/db/database.py
cat > app/db/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

# Create app/main.py
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}

@app.get("/api/v1/")
def root():
    return {"message": "AI Agent Hub API", "version": settings.api_version}
EOF

# Create models/__init__.py
touch app/models/__init__.py

# Create schemas/__init__.py
touch app/schemas/__init__.py

# Create api/__init__.py
touch app/api/__init__.py

# Create api/agents.py (placeholder)
cat > app/api/agents.py << 'EOF'
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

@router.get("/")
def list_agents():
    return {"agents": [], "total": 0}
EOF

# Create api/mcp_servers.py (placeholder)
cat > app/api/mcp_servers.py << 'EOF'
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/mcp-servers", tags=["mcp-servers"])

@router.get("/")
def list_mcp_servers():
    return {"mcp_servers": [], "total": 0}
EOF

# Create services/__init__.py
touch app/services/__init__.py

# Create core/__init__.py
touch app/core/__init__.py

# Create core/security.py (placeholder)
cat > app/core/security.py << 'EOF'
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt
EOF

# Create tests/__init__.py
touch tests/__init__.py

# Create tests/test_health.py
cat > tests/test_health.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
EOF

# Create backend README
cat > README.md << 'EOF'
# AI Agent Hub - Backend

FastAPI-based backend for AI Agent Hub platform.

## Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

## Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database Migrations

```bash
alembic upgrade head
```

## Tests

```bash
pytest
pytest --cov=app tests/
```

## Code Quality

```bash
black .
flake8 .
mypy .
isort .
```

## API Documentation

Visit: http://localhost:8000/docs (Swagger UI)
EOF

cd ..

echo "✅ Backend setup complete"
```

## Step 4: Setup Frontend (Angular with TailwindCSS)

```bash
# Ensure Node.js and npm are installed
node --version
npm --version

# Check if Angular CLI is installed globally, if not install it
npm list -g @angular/cli > /dev/null 2>&1 || npm install -g @angular/cli@latest

# Create Angular project
ng new frontend --routing --style=css --skip-git=true

cd frontend

# Add TailwindCSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Configure tailwind.config.js
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

# Add Tailwind directives to styles.css
cat > src/styles.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF

# Create frontend README
cat > README.md << 'EOF'
# AI Agent Hub - Frontend

Angular + TailwindCSS frontend for AI Agent Hub platform.

## Development Server

```bash
npm install
ng serve
```

Navigate to `http://localhost:4200/`.

## Build

```bash
ng build
```

## Code Generation

```bash
# Generate component
ng generate component components/agent-card

# Generate service
ng generate service services/agent
```

## Code Quality

```bash
ng lint
```

## Testing

```bash
ng test
```

## API Integration

API endpoints are available at `http://localhost:8000/api/v1`
EOF

# Update angular.json to use Tailwind
sed -i '' 's/"styles": \[/"styles": [\n            "src\/tailwind.css",/' angular.json

cd ..

echo "✅ Frontend setup complete"
```

## Step 5: Create Docker Setup

```bash
# Create docker-compose.yml in project root
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: ai_agent_hub_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ai_agent_hub
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ai_agent_hub_backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/ai_agent_hub
      ENVIRONMENT: development
      DEBUG: "true"
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: ai_agent_hub_frontend
    ports:
      - "4200:4200"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      ANGULAR_CLI_CACHE: /tmp/.ng
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
EOF

# Create Dockerfile for backend
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create Dockerfile for frontend development
cat > frontend/Dockerfile.dev << 'EOF'
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 4200

CMD ["ng", "serve", "--host", "0.0.0.0"]
EOF

# Create .dockerignore for backend
cat > backend/.dockerignore << 'EOF'
.venv
__pycache__
*.pyc
.pytest_cache
.coverage
.env
.env.local
.DS_Store
*.log
EOF

# Create .dockerignore for frontend
cat > frontend/.dockerignore << 'EOF'
node_modules
dist
.angular
.git
.gitignore
README.md
.env
.env.local
EOF

echo "✅ Docker setup complete"
```

## Step 6: Verify Directory Structure

```bash
# From ai-agent-hub root directory
tree -L 3 -I 'node_modules|__pycache__|.venv' 

# If tree is not installed, use this instead:
find . -type d -not -path '*/\.*' -not -path '*/node_modules*' -not -path '*/.venv*' -not -path '*/__pycache__*' | head -50
```

## Step 7: Initialize Git and Create Initial Commit

```bash
cd path/to/your/workspace/ai-agent-hub

git add .
git commit -m "feat: Initialize project structure with FastAPI backend, Angular frontend, and documentation"

# View commit log
git log --oneline
```

## Step 8: Verify Backend Setup (Optional Test)

```bash
cd backend

# Activate virtual environment
source .venv/bin/activate

# Run health check
pytest tests/test_health.py -v

echo "✅ Backend tests passed"
```

## Final Directory Structure

Your project should look like this:

```
ai-agent-hub/
├── backend/
│   ├── .venv/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── agents.py
│   │   │   └── mcp_servers.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   └── services/
│   │       └── __init__.py
│   ├── migrations/
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_health.py
│   ├── .env
│   ├── .env.example
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── README.md
│   └── requirements.txt
├── frontend/
│   ├── node_modules/
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.component.ts
│   │   │   ├── app.component.html
│   │   │   └── app.component.css
│   │   ├── assets/
│   │   ├── styles.css
│   │   └── main.ts
│   ├── .dockerignore
│   ├── Dockerfile.dev
│   ├── angular.json
│   ├── package.json
│   ├── README.md
│   ├── tailwind.config.js
│   └── tsconfig.json
├── docs/
│   └── requirements.md
├── scripts/
├── .gitignore
├── README.md
└── docker-compose.yml
```

## Next Steps

1. Review `docs/requirements.md` for detailed specifications
2. Start backend server: `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload`
3. Start frontend server: `cd frontend && ng serve`
4. Or use Docker Compose: `docker-compose up`
5. Backend API docs: http://localhost:8000/docs
6. Frontend: http://localhost:4200

---

**Note**: Update `.env` and `.env.example` with your actual configuration values before deploying to production.
