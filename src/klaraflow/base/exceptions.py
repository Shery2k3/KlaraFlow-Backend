from typing import List, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .responses import ErrorResponse

class APIException(Exception):
    """
    Custom exception class that can be raised to return a standardized error response.
    """
    def __init__(
        self,
        status_code: int,
        message: str,
        errors: Optional[List[str]] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.errors = errors if errors else []

async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    Handles our custom APIException and returns a standardized error response.
    """
    content = ErrorResponse(message=exc.message, errors=exc.errors).model_dump(exclude_none=True)
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handles Pydantic's RequestValidationError and formats it into our standardized error response.
    """
    error_messages: List[str] = []
    for error in exc.errors():
        field = " -> ".join(map(str, error["loc"]))
        message = error["msg"]
        error_messages.append(f"Field '{field}': {message}")

    content = ErrorResponse(
        message="Validation failed. Please check the provided data.",
        errors=error_messages
    ).model_dump()
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=content,
    )