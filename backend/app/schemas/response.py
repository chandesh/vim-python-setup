from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper.
    
    Provides a consistent response format across all endpoints.
    
    Attributes:
        success: Whether the request was successful
        data: Response data (generic type)
        message: Optional message for additional context
    """
    
    success: bool = Field(default=True, description="Request success status")
    data: Optional[T] = Field(default=None, description="Response data")
    message: Optional[str] = Field(default=None, description="Optional message")


class ErrorResponse(BaseModel):
    """Error response schema.
    
    Used for error responses with detailed error information.
    
    Attributes:
        success: Always False for errors
        error: Error type or code
        message: Human-readable error message
        details: Optional additional error details
    """
    
    success: bool = Field(default=False, description="Request success status")
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")
