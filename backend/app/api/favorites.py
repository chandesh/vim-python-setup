"""Favorites API endpoints (all require authentication)."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.favorite import (
    FavoriteCheckResponse,
    FavoriteCreate,
    FavoriteItemResponse,
    FavoriteListResponse,
)
from app.schemas.response import ApiResponse
from app.services import favorite_service
from app.services.favorite_service import (
    DuplicateFavoriteError,
    FavoriteItemNotFoundError,
    FavoriteTargetNotFoundError,
)

router = APIRouter(prefix="/api/v1/favorites", tags=["favorites"])


@router.get("", response_model=ApiResponse[FavoriteListResponse])
def list_favorites(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the authenticated user's favorites, newest first."""
    favorites, total = favorite_service.list_favorites(db, current_user, page, limit)
    return ApiResponse(
        success=True,
        data=FavoriteListResponse(
            favorites=[favorite_service.to_favorite_item(f) for f in favorites],
            total=total,
            page=page,
            limit=limit,
        ),
    )


@router.post("", response_model=ApiResponse[FavoriteItemResponse], status_code=status.HTTP_201_CREATED)
def add_favorite(
    data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add an agent or MCP server to favorites.

    Body must contain exactly one of `agent_id` or `mcp_server_id`.

    Raises:
        404: Target agent/server not found
        409: Already favorited
    """
    try:
        favorite = favorite_service.add_favorite(db, current_user, data)
    except FavoriteTargetNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateFavoriteError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return ApiResponse(
        success=True,
        data=favorite_service.to_favorite_item(favorite),
        message="Added to favorites",
    )


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    favorite_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a favorite by ID.

    Raises:
        404: Favorite does not exist or belongs to another user
    """
    try:
        favorite_service.remove_favorite(db, current_user, favorite_id)
    except FavoriteItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return None


@router.get("/check", response_model=ApiResponse[FavoriteCheckResponse])
def check_favorite(
    agent_id: UUID | None = Query(None, description="Agent ID to check"),
    mcp_server_id: UUID | None = Query(None, description="MCP server ID to check"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check whether an item is favorited by the authenticated user.

    Provide exactly one of `agent_id` or `mcp_server_id`.
    """
    if bool(agent_id) == bool(mcp_server_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide exactly one of agent_id or mcp_server_id",
        )

    result = favorite_service.check_favorite(db, current_user, agent_id, mcp_server_id)
    return ApiResponse(success=True, data=result)
