"""Favorites business logic."""
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.models.agent import Agent
from app.models.favorite import UserFavorite
from app.models.mcp_server import MCPServer
from app.models.user import User
from app.schemas.favorite import (
    FavoriteCheckResponse,
    FavoriteCreate,
    FavoriteItemResponse,
)
from app.schemas.agent import AgentSummary
from app.schemas.mcp_server import MCPServerSummary


class FavoriteItemNotFoundError(Exception):
    """Raised when a favorite does not exist for the user."""


class FavoriteTargetNotFoundError(Exception):
    """Raised when the agent/server to favorite does not exist."""


class DuplicateFavoriteError(Exception):
    """Raised when the item is already favorited by the user."""


def _load_options():
    return (
        joinedload(UserFavorite.agent).options(
            joinedload(Agent.category),
            joinedload(Agent.tags),
        ),
        joinedload(UserFavorite.mcp_server).options(
            joinedload(MCPServer.category),
            joinedload(MCPServer.tags),
        ),
    )


def list_favorites(db: Session, user: User, page: int = 1, limit: int = 20):
    """Return the user's favorites, newest first, with hydrated item summaries."""
    query = db.query(UserFavorite).filter(
        UserFavorite.user_id == user.id
    ).options(*_load_options())

    total = query.count()
    favorites = (
        query.order_by(UserFavorite.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return favorites, total


def to_favorite_item(favorite: UserFavorite) -> FavoriteItemResponse:
    """Convert a UserFavorite ORM object into its API response shape."""
    return FavoriteItemResponse(
        id=favorite.id,
        created_at=favorite.created_at,
        agent=AgentSummary.model_validate(favorite.agent) if favorite.agent_id else None,
        mcp_server=MCPServerSummary.model_validate(favorite.mcp_server) if favorite.mcp_server_id else None,
    )


def add_favorite(db: Session, user: User, data: FavoriteCreate) -> UserFavorite:
    """Add an agent or MCP server to the user's favorites.

    Raises:
        FavoriteTargetNotFoundError: Target agent/server does not exist
        DuplicateFavoriteError: Already favorited by this user
    """
    # Verify the target exists before creating the link
    if data.agent_id:
        target = db.query(Agent).filter(Agent.id == data.agent_id).first()
        if not target:
            raise FavoriteTargetNotFoundError("Agent not found")
    else:
        target = db.query(MCPServer).filter(MCPServer.id == data.mcp_server_id).first()
        if not target:
            raise FavoriteTargetNotFoundError("MCP server not found")

    # Enforce uniqueness per user/target pair
    existing_query = db.query(UserFavorite).filter(UserFavorite.user_id == user.id)
    if data.agent_id:
        existing_query = existing_query.filter(UserFavorite.agent_id == data.agent_id)
    else:
        existing_query = existing_query.filter(UserFavorite.mcp_server_id == data.mcp_server_id)

    if existing_query.first():
        raise DuplicateFavoriteError("Already in favorites")

    favorite = UserFavorite(
        user_id=user.id,
        agent_id=data.agent_id,
        mcp_server_id=data.mcp_server_id,
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def remove_favorite(db: Session, user: User, favorite_id: UUID) -> None:
    """Remove one of the user's favorites.

    Raises:
        FavoriteItemNotFoundError: No such favorite owned by this user
    """
    favorite = db.query(UserFavorite).filter(
        UserFavorite.id == favorite_id,
        UserFavorite.user_id == user.id,
    ).first()

    if not favorite:
        raise FavoriteItemNotFoundError("Favorite not found")

    db.delete(favorite)
    db.commit()


def check_favorite(
    db: Session,
    user: User,
    agent_id: UUID | None = None,
    mcp_server_id: UUID | None = None,
) -> FavoriteCheckResponse:
    """Check whether the user has favorited the given agent or server."""
    query = db.query(UserFavorite).filter(UserFavorite.user_id == user.id)
    if agent_id:
        query = query.filter(UserFavorite.agent_id == agent_id)
    elif mcp_server_id:
        query = query.filter(UserFavorite.mcp_server_id == mcp_server_id)

    favorite = query.first()
    return FavoriteCheckResponse(is_favorited=favorite is not None, favorite_id=favorite.id if favorite else None)
