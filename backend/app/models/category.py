from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Category(Base):
    """Category model for organizing agents and MCP servers.
    
    Categories represent high-level classifications like 'Productivity',
    'Development', 'Data Analysis', etc.
    
    Attributes:
        id: Unique identifier (UUID)
        name: Display name of the category
        slug: URL-friendly version of the name
        description: Detailed description of the category
        icon_url: Optional URL to category icon
        created_at: Timestamp when category was created
        updated_at: Timestamp when category was last updated
    """
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    agents = relationship("Agent", back_populates="category")
    mcp_servers = relationship("MCPServer", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"
