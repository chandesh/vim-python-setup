from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps."""
    
    created_at: datetime
    updated_at: datetime


class IDMixin(BaseModel):
    """Mixin for UUID identifier."""
    
    id: UUID
