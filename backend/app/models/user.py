from sqlalchemy import Column, String, Text, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration for access control."""
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(Base):
    """User model for authentication and user management.
    
    Supports both traditional email/password authentication and OAuth providers.
    
    Attributes:
        id: Unique identifier (UUID)
        email: User's email address (unique)
        username: User's username (unique)
        password_hash: Hashed password (null for OAuth-only users)
        oauth_provider: OAuth provider name (google, github, etc.)
        oauth_id: User ID from OAuth provider
        avatar_url: URL to user's avatar image
        bio: User's bio/description
        role: User role (user, moderator, admin)
        is_active: Whether user account is active
        created_at: Timestamp when user registered
        updated_at: Timestamp when user info was last updated
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    oauth_provider = Column(String(50), nullable=True)
    oauth_id = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    comparisons = relationship("Comparison", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"
