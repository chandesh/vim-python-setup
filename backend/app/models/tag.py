from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Tag(Base):
    """Tag model for fine-grained classification of agents and MCP servers.
    
    Tags provide flexible, multi-dimensional categorization beyond primary
    categories. Examples: 'machine-learning', 'api-integration', 'automation'.
    
    Attributes:
        id: Unique identifier (UUID)
        name: Display name of the tag
        slug: URL-friendly version of the name
        description: Optional description of what this tag represents
        created_at: Timestamp when tag was created
    """
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    agents = relationship("Agent", secondary="agent_tags", back_populates="tags")
    mcp_servers = relationship("MCPServer", secondary="mcp_server_tags", back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.name}>"
