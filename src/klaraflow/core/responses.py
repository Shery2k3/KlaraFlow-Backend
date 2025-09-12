from typing import TypeVar, Generic, Optional, List, Dict, Any
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response schema that matches the frontend's ApiResponse interface."""
    success: bool = Field(default=True)
    data: Optional[T] = None
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standard error response schema that matches the frontend's ApiResponse interface."""
    success: bool = Field(default=False)
    data: Optional[T] = None
    errors: Optional[List[str]] = None
    message: str = "An error occurred."

def create_response(
    data: Optional[T] = None,
    message: Optional[str] = None,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """
    A utility function to create a standardized JSON success response.
    This allows us to set custom status codes while maintaining a consistent response body.
    """
    content = SuccessResponse(data=data, message=message).model_dump(exclude_none=True)
    return JSONResponse(
        status_code=status_code,
        content=content
    )