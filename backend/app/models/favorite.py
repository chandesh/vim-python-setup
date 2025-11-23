from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class UserFavorite(Base):
    """User favorites for agents and MCP servers.
    
    Allows users to bookmark/save agents or MCP servers for quick access.
    Each favorite links to either an agent OR an mcp_server (not both).
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to User
        agent_id: Foreign key to Agent (nullable, one of agent_id/mcp_server_id required)
        mcp_server_id: Foreign key to MCPServer (nullable, one of agent_id/mcp_server_id required)
        created_at: Timestamp when favorite was added
    """
    __tablename__ = "user_favorites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id', ondelete='CASCADE'), nullable=True, index=True)
    mcp_server_id = Column(UUID(as_uuid=True), ForeignKey('mcp_servers.id', ondelete='CASCADE'), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="favorites")
    agent = relationship("Agent", back_populates="favorites")
    mcp_server = relationship("MCPServer", back_populates="favorites")

    def __repr__(self):
        item_type = "Agent" if self.agent_id else "MCPServer"
        item_id = self.agent_id or self.mcp_server_id
        return f"<UserFavorite user={self.user_id} {item_type}={item_id}>"
