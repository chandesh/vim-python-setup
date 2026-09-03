from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import Optional
from uuid import UUID
from datetime import date

from app.api.date_filter import apply_created_at_range, validate_date_range
from app.db.database import get_db
from app.core.dependencies import get_optional_user
from app.models.agent import Agent
from app.models.tag import Tag
from app.models.user import User
from app.schemas.agent import (
    AgentCreate,
    AgentDetailResponse,
    AgentSummary,
    AgentUpdate,
    AgentResponse,
    AgentListResponse,
    AgentSearchParams,
)
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.get("", response_model=ApiResponse[AgentListResponse])
def list_agents(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    pricing_model: Optional[str] = Query(None, description="Filter by pricing model"),
    featured: Optional[bool] = Query(None, description="Filter featured agents"),
    date_from: Optional[date] = Query(None, description="Only items created on or after this date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Only items created on or before this date (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("created_at", description="Sort by field (name, created_at, view_count)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    """List all agents with pagination, filtering, and sorting.
    
    Supports filtering by category, pricing model, and featured status.
    Supports sorting by name, created_at, or view_count.
    Guests (unauthenticated) only see a capped 3-item preview.
    """
    query = db.query(Agent).options(
        joinedload(Agent.category),
        joinedload(Agent.tags)
    )

    # Apply filters
    if category_id:
        query = query.filter(Agent.category_id == category_id)
    if pricing_model:
        query = query.filter(Agent.pricing_model == pricing_model)
    if featured is not None:
        query = query.filter(Agent.featured == featured)

    validate_date_range(date_from, date_to)
    if date_from or date_to:
        query = apply_created_at_range(query, Agent, date_from, date_to)

    # Get total count
    total = query.count()
    
    # Apply sorting
    sort_fields = {
        "name": Agent.name,
        "created_at": Agent.created_at,
        "view_count": Agent.view_count
    }
    sort_field = sort_fields.get(sort_by, Agent.created_at)
    query = query.order_by(sort_field.desc() if sort_order == "desc" else sort_field.asc())

    # Guests: cap preview window at 3 items regardless of requested page/limit
    effective_limit = limit
    is_guest_preview = False
    if current_user is None:
        is_guest_preview = True
        effective_limit = min(limit, 3)
        page = 1
    
    # Get paginated results
    agents = query\
        .offset((page - 1) * limit)\
        .limit(effective_limit)\
        .all()
    
    return ApiResponse(
        success=True,
        data=AgentListResponse(
            agents=agents,
            total=total,
            page=page,
            limit=effective_limit,
            is_guest_preview=is_guest_preview
        )
    )


@router.get("/search", response_model=ApiResponse[AgentListResponse])
def search_agents(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query("view_count", description="Sort by field (name, created_at, view_count)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    date_from: Optional[date] = Query(None, description="Only items created on or after this date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Only items created on or before this date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    """Search agents by name or description.
    
    Args:
        q: Search query string
        page: Page number
        limit: Items per page
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        Paginated list of matching agents.
        Guests only see a capped 3-item preview.
    """
    # Search in name, short_description, and description
    search_filter = or_(
        Agent.name.ilike(f"%{q}%"),
        Agent.short_description.ilike(f"%{q}%"),
        Agent.description.ilike(f"%{q}%")
    )
    
    query = db.query(Agent).options(
        joinedload(Agent.category),
        joinedload(Agent.tags)
    ).filter(search_filter)
    validate_date_range(date_from, date_to)
    if date_from or date_to:
        query = apply_created_at_range(query, Agent, date_from, date_to)
    total = query.count()
    
    # Apply sorting
    sort_fields = {
        "name": Agent.name,
        "created_at": Agent.created_at,
        "view_count": Agent.view_count
    }
    sort_field = sort_fields.get(sort_by, Agent.view_count)
    query = query.order_by(sort_field.desc() if sort_order == "desc" else sort_field.asc())

    # Guests: cap preview window at 3 items regardless of requested page/limit
    effective_limit = limit
    is_guest_preview = False
    if current_user is None:
        is_guest_preview = True
        effective_limit = min(limit, 3)
        page = 1
    
    agents = query\
        .offset((page - 1) * limit)\
        .limit(effective_limit)\
        .all()
    
    return ApiResponse(
        success=True,
        data=AgentListResponse(
            agents=agents,
            total=total,
            page=page,
            limit=effective_limit,
            is_guest_preview=is_guest_preview
        )
    )


@router.get("/{agent_id}")
def get_agent(
    agent_id: UUID,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    """Get a specific agent by ID.

    Also increments the view count for the agent and returns
    related agents from the same category.

    Guests (unauthenticated) receive a restricted teaser with identity
    fields only — no description, tags, related agents, or view inflation.

    Args:
        agent_id: UUID of the agent to retrieve

    Returns:
        Agent details with related agents, or a restricted guest teaser

    Raises:
        404: Agent not found
    """
    agent = db.query(Agent).options(
        joinedload(Agent.category),
        joinedload(Agent.tags)
    ).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )

    # Guests: teaser only, no view-count inflation
    if current_user is None:
        return {
            "success": True,
            "data": {
                "restricted": True,
                "agent": {
                    "id": agent.id,
                    "name": agent.name,
                    "slug": agent.slug,
                    "short_description": agent.short_description,
                    "logo_url": agent.logo_url,
                    "pricing_model": agent.pricing_model.value,
                    "featured": agent.featured,
                    "category": {"id": agent.category.id, "name": agent.category.name} if agent.category else None,
                    "view_count": agent.view_count,
                    "created_at": agent.created_at,
                },
            },
        }

    # Increment view count
    agent.view_count += 1
    db.commit()
    db.refresh(agent)

    # Related agents from the same category (excluding current), most viewed first
    related_agents = db.query(Agent).options(
        joinedload(Agent.category),
        joinedload(Agent.tags)
    ).filter(
        Agent.category_id == agent.category_id,
        Agent.id != agent.id
    ).order_by(Agent.view_count.desc()).limit(4).all()

    detail = AgentDetailResponse.model_validate(agent)
    detail.related_agents = [AgentSummary.model_validate(a) for a in related_agents]

    return ApiResponse(success=True, data=detail)


@router.post("", response_model=ApiResponse[AgentResponse], status_code=status.HTTP_201_CREATED)
def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db)
):
    """Create a new agent.
    
    Args:
        agent_data: Agent creation data including tag IDs
        
    Returns:
        Created agent
        
    Raises:
        400: Agent with same slug already exists
        404: Category or tags not found
    """
    # Check if slug already exists
    existing = db.query(Agent).filter(Agent.slug == agent_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent with slug '{agent_data.slug}' already exists"
        )
    
    # Extract tag_ids and create agent without them
    tag_ids = agent_data.tag_ids
    agent_dict = agent_data.model_dump(exclude={'tag_ids'})
    
    # Create new agent
    agent = Agent(**agent_dict)
    
    # Add tags if provided
    if tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        if len(tags) != len(tag_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more tag IDs not found"
            )
        agent.tags = tags
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return ApiResponse(
        success=True,
        data=agent,
        message="Agent created successfully"
    )


@router.put("/{agent_id}", response_model=ApiResponse[AgentResponse])
def update_agent(
    agent_id: UUID,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing agent.
    
    Args:
        agent_id: UUID of the agent to update
        agent_data: Updated agent data
        
    Returns:
        Updated agent
        
    Raises:
        404: Agent not found
        400: Slug already exists
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )
    
    # Check slug uniqueness if being updated
    if agent_data.slug and agent_data.slug != agent.slug:
        existing = db.query(Agent).filter(Agent.slug == agent_data.slug).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent with slug '{agent_data.slug}' already exists"
            )
    
    # Handle tag updates
    update_data = agent_data.model_dump(exclude_unset=True, exclude={'tag_ids'})
    
    if agent_data.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(agent_data.tag_ids)).all()
        if len(tags) != len(agent_data.tag_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more tag IDs not found"
            )
        agent.tags = tags
    
    # Update other fields
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    db.commit()
    db.refresh(agent)
    
    return ApiResponse(
        success=True,
        data=agent,
        message="Agent updated successfully"
    )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(
    agent_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an agent.
    
    Args:
        agent_id: UUID of the agent to delete
        
    Raises:
        404: Agent not found
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )
    
    db.delete(agent)
    db.commit()
    
    return None
