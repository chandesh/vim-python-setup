from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Comparison(Base):
    """Comparison list model for side-by-side comparisons.
    
    Users can create comparison lists to compare multiple agents or MCP servers.
    Lists can be private (user-only) or public (shareable).
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to User who created the comparison
        title: Name/title of the comparison
        description: Optional description of what's being compared
        is_public: Whether comparison is publicly accessible
        created_at: Timestamp when comparison was created
        updated_at: Timestamp when comparison was last modified
    """
    __tablename__ = "comparisons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="comparisons")
    items = relationship("ComparisonItem", back_populates="comparison", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Comparison {self.title} by user={self.user_id}>"


class ComparisonItem(Base):
    """Individual items within a comparison list.
    
    Each item represents one agent or MCP server in the comparison.
    Items are ordered within the comparison.
    
    Attributes:
        id: Unique identifier (UUID)
        comparison_id: Foreign key to Comparison
        agent_id: Foreign key to Agent (nullable, one of agent_id/mcp_server_id required)
        mcp_server_id: Foreign key to MCPServer (nullable, one of agent_id/mcp_server_id required)
        order: Position in the comparison list
    """
    __tablename__ = "comparison_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comparison_id = Column(UUID(as_uuid=True), ForeignKey('comparisons.id', ondelete='CASCADE'), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id', ondelete='CASCADE'), nullable=True)
    mcp_server_id = Column(UUID(as_uuid=True), ForeignKey('mcp_servers.id', ondelete='CASCADE'), nullable=True)
    order = Column(Integer, nullable=False, default=0)

    # Relationships
    comparison = relationship("Comparison", back_populates="items")

    def __repr__(self):
        item_type = "Agent" if self.agent_id else "MCPServer"
        item_id = self.agent_id or self.mcp_server_id
        return f"<ComparisonItem {item_type}={item_id} order={self.order}>"
