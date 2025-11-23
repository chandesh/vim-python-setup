from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from uuid import UUID

from app.db.database import get_db
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("", response_model=ApiResponse[CategoryListResponse])
def list_categories(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """List all categories with pagination.
    
    Returns a paginated list of all categories in the system.
    """
    # Get total count
    total = db.query(func.count(Category.id)).scalar()
    
    # Get paginated results
    categories = db.query(Category)\
        .order_by(Category.name)\
        .offset((page - 1) * limit)\
        .limit(limit)\
        .all()
    
    return ApiResponse(
        success=True,
        data=CategoryListResponse(
            categories=categories,
            total=total,
            page=page,
            limit=limit
        )
    )


@router.get("/{category_id}", response_model=ApiResponse[CategoryResponse])
def get_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific category by ID.
    
    Args:
        category_id: UUID of the category to retrieve
        
    Returns:
        Category details
        
    Raises:
        404: Category not found
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    
    return ApiResponse(success=True, data=category)


@router.post("", response_model=ApiResponse[CategoryResponse], status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new category.
    
    Args:
        category_data: Category creation data
        
    Returns:
        Created category
        
    Raises:
        400: Category with same slug already exists
    """
    # Check if slug already exists
    existing = db.query(Category).filter(Category.slug == category_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with slug '{category_data.slug}' already exists"
        )
    
    # Create new category
    category = Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return ApiResponse(
        success=True,
        data=category,
        message="Category created successfully"
    )


@router.put("/{category_id}", response_model=ApiResponse[CategoryResponse])
def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing category.
    
    Args:
        category_id: UUID of the category to update
        category_data: Updated category data
        
    Returns:
        Updated category
        
    Raises:
        404: Category not found
        400: Slug already exists
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    
    # Check slug uniqueness if being updated
    if category_data.slug and category_data.slug != category.slug:
        existing = db.query(Category).filter(Category.slug == category_data.slug).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with slug '{category_data.slug}' already exists"
            )
    
    # Update fields
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return ApiResponse(
        success=True,
        data=category,
        message="Category updated successfully"
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a category.
    
    Args:
        category_id: UUID of the category to delete
        
    Raises:
        404: Category not found
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    
    db.delete(category)
    db.commit()
    
    return None
