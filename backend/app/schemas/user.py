from pydantic import Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.schemas.base import BaseSchema, IDMixin, TimestampMixin
from app.models.user import UserRole

EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


class UserCreate(BaseSchema):
    """Schema for user registration."""

    email: str = Field(..., max_length=255, description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 chars)")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        import re
        v = v.strip().lower()
        if not re.match(EMAIL_PATTERN, v):
            raise ValueError("Invalid email address format")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        import re
        v = v.strip()
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username may only contain letters, numbers, underscores and hyphens")
        return v


class UserLogin(BaseSchema):
    """Schema for user login."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseSchema, IDMixin, TimestampMixin):
    """Public user representation returned by the API."""

    email: str = Field(..., max_length=255)
    username: str = Field(..., max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None
    role: UserRole
    is_active: bool


class Token(BaseSchema):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token lifetime in seconds")


class TokenData(BaseSchema):
    """Payload extracted from a validated JWT."""

    sub: str = Field(..., description="User ID from the token subject claim")
