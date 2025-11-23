from pydantic import Field
from typing import Optional

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


class CategoryBase(BaseSchema):
    """Base schema for Category with common fields."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly slug")
    description: str = Field(..., description="Category description")
    icon_url: Optional[str] = Field(None, max_length=500, description="URL to category icon")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryUpdate(BaseSchema):
    """Schema for updating a category."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon_url: Optional[str] = Field(None, max_length=500)


class CategoryResponse(CategoryBase, IDMixin, TimestampMixin):
    """Schema for category response."""
    pass


class CategoryListResponse(BaseSchema):
    """Schema for paginated category list response."""
    
    categories: list[CategoryResponse]
    total: int
    page: int
    limit: int
