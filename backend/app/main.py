from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import categories, agents, mcp_servers, auth, favorites

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug,
    description="AI Agent Hub API - Discover and compare AI agents and MCP servers"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(categories.router)
app.include_router(agents.router)
app.include_router(mcp_servers.router)
app.include_router(auth.router)
app.include_router(favorites.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
        "version": settings.api_version
    }


@app.get("/api/v1/")
def root():
    return {
        "message": "AI Agent Hub API",
        "version": settings.api_version,
        "docs": "/docs"
    }
