from pydantic import Field
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin
from app.models.mcp_server import ServerScope


class MCPServerSummary(BaseSchema, IDMixin, TimestampMixin):
    """Compact MCP server card used in related/favorites sections."""

    name: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    description: str
    language: str = Field(..., max_length=50)
    logo_url: str | None = Field(None, max_length=500)
    star_count: int
    scope: ServerScope
