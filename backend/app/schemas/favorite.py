from pydantic import Field, model_validator
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.schemas.base import BaseSchema
from app.schemas.agent import AgentSummary
from app.schemas.mcp_server import MCPServerSummary


class FavoriteCreate(BaseSchema):
    """Payload for adding a favorite. Provide exactly one target."""

    agent_id: Optional[UUID] = Field(None, description="Agent to favorite")
    mcp_server_id: Optional[UUID] = Field(None, description="MCP server to favorite")

    @model_validator(mode="after")
    def check_single_target(self) -> "FavoriteCreate":
        if bool(self.agent_id) == bool(self.mcp_server_id):
            raise ValueError("Provide exactly one of agent_id or mcp_server_id")
        return self


class FavoriteItemResponse(BaseSchema):
    """A favorite entry with the hydrated item summary."""

    id: UUID = Field(..., description="Favorite ID (used for removal)")
    created_at: datetime
    agent: Optional[AgentSummary] = None
    mcp_server: Optional[MCPServerSummary] = None


class FavoriteListResponse(BaseSchema):
    """Paginated list of the user's favorites."""

    favorites: list[FavoriteItemResponse]
    total: int
    page: int
    limit: int


class FavoriteCheckResponse(BaseSchema):
    """Result of a favorite status check."""

    is_favorited: bool
    favorite_id: Optional[UUID] = None
