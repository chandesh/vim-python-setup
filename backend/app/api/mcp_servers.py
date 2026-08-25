"""MCP Servers API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from typing import Optional
from uuid import UUID

from app.db.database import get_db
from app.models.mcp_server import MCPServer, ServerScope
from app.models.category import Category
from app.models.tag import Tag

router = APIRouter(prefix="/api/mcp-servers", tags=["mcp-servers"])


@router.get("")
async def get_mcp_servers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(12, ge=1, le=100, description="Items per page"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    language: Optional[str] = Query(None, description="Filter by programming language"),
    scope: Optional[ServerScope] = Query(None, description="Filter by scope (local/cloud/hybrid)"),
    featured: Optional[bool] = Query(None, description="Filter by featured status"),
    sort_by: Optional[str] = Query("star_count", description="Sort by field (name, created_at, star_count, view_count)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db)
):
    """Get list of MCP servers with pagination, filters, and sorting."""
    try:
        # Base query with eager loading
        query = db.query(MCPServer).options(
            joinedload(MCPServer.category),
            joinedload(MCPServer.tags)
        )
        
        # Apply filters
        if category_id:
            query = query.filter(MCPServer.category_id == category_id)
        
        if language:
            query = query.filter(MCPServer.language.ilike(f"%{language}%"))
        
        if scope:
            query = query.filter(MCPServer.scope == scope)
        
        if featured is not None:
            query = query.filter(MCPServer.featured == featured)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_fields = {
            "name": MCPServer.name,
            "created_at": MCPServer.created_at,
            "star_count": MCPServer.star_count,
            "view_count": MCPServer.view_count
        }
        sort_field = sort_fields.get(sort_by, MCPServer.star_count)
        query = query.order_by(sort_field.desc() if sort_order == "desc" else sort_field.asc())
        
        # Apply pagination
        offset = (page - 1) * limit
        servers = query.offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "servers": servers,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_mcp_servers(
    query: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(12, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query("star_count", description="Sort by field (name, created_at, star_count, view_count)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db)
):
    """Search MCP servers by name, description, or language with sorting."""
    try:
        # Search query with eager loading
        search_filter = or_(
            MCPServer.name.ilike(f"%{query}%"),
            MCPServer.description.ilike(f"%{query}%"),
            MCPServer.language.ilike(f"%{query}%")
        )
        
        db_query = db.query(MCPServer).options(
            joinedload(MCPServer.category),
            joinedload(MCPServer.tags)
        ).filter(search_filter)
        
        # Get total count
        total = db_query.count()
        
        # Apply sorting
        sort_fields = {
            "name": MCPServer.name,
            "created_at": MCPServer.created_at,
            "star_count": MCPServer.star_count,
            "view_count": MCPServer.view_count
        }
        sort_field = sort_fields.get(sort_by, MCPServer.star_count)
        db_query = db_query.order_by(sort_field.desc() if sort_order == "desc" else sort_field.asc())
        
        # Apply pagination
        offset = (page - 1) * limit
        servers = db_query.offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "servers": servers,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}")
async def get_mcp_server(
    server_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a single MCP server by ID.

    Also increments the view count and returns related servers
    sharing the same category or language.
    """
    try:
        server = db.query(MCPServer).options(
            joinedload(MCPServer.category),
            joinedload(MCPServer.tags)
        ).filter(MCPServer.id == server_id).first()

        if not server:
            raise HTTPException(status_code=404, detail="MCP Server not found")

        # Increment view count
        server.view_count += 1
        db.commit()

        # Related servers from the same category or language, most starred first
        related_servers = db.query(MCPServer).options(
            joinedload(MCPServer.category),
            joinedload(MCPServer.tags)
        ).filter(
            MCPServer.id != server.id,
            or_(
                MCPServer.category_id == server.category_id,
                func.lower(MCPServer.language) == func.lower(server.language)
            )
        ).order_by(MCPServer.star_count.desc()).limit(4).all()

        return {
            "success": True,
            "data": {
                "server": server,
                "related_servers": related_servers
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages/list")
async def get_languages(db: Session = Depends(get_db)):
    """Get list of unique programming languages."""
    try:
        languages = db.query(MCPServer.language).distinct().order_by(MCPServer.language).all()
        language_list = [lang[0] for lang in languages if lang[0]]
        
        return {
            "success": True,
            "data": {
                "languages": language_list
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
