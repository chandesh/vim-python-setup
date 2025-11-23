from pydantic import Field, HttpUrl
from typing import Optional
from uuid import UUID

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin
from app.models.agent import PricingModel


class AgentBase(BaseSchema):
    """Base schema for Agent with common fields."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Agent name")
    slug: str = Field(..., min_length=1, max_length=200, description="URL-friendly slug")
    description: str = Field(..., description="Full description of the agent")
    short_description: str = Field(..., max_length=160, description="Brief description for previews")
    website_url: str = Field(..., description="Official website URL")
    category_id: UUID = Field(..., description="Category ID")
    pricing_model: PricingModel = Field(default=PricingModel.FREE, description="Pricing model")
    logo_url: Optional[str] = Field(None, max_length=500, description="Logo/icon URL")


class AgentCreate(AgentBase):
    """Schema for creating a new agent."""
    
    tag_ids: list[UUID] = Field(default=[], description="List of tag IDs")


class AgentUpdate(BaseSchema):
    """Schema for updating an agent."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=160)
    website_url: Optional[str] = None
    category_id: Optional[UUID] = None
    pricing_model: Optional[PricingModel] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    featured: Optional[bool] = None
    tag_ids: Optional[list[UUID]] = None


class AgentResponse(AgentBase, IDMixin, TimestampMixin):
    """Schema for agent response."""
    
    featured: bool
    view_count: int
    # category: Optional["CategoryResponse"] = None  # Can be added with forward ref
    # tags: list["TagResponse"] = []  # Can be added with forward ref


class AgentListResponse(BaseSchema):
    """Schema for paginated agent list response."""
    
    agents: list[AgentResponse]
    total: int
    page: int
    limit: int


class AgentSearchParams(BaseSchema):
    """Schema for agent search/filter parameters."""
    
    q: Optional[str] = Field(None, description="Search query")
    category_id: Optional[UUID] = Field(None, description="Filter by category")
    pricing_model: Optional[PricingModel] = Field(None, description="Filter by pricing model")
    featured: Optional[bool] = Field(None, description="Filter featured agents")
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
