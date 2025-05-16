"""
Custom exceptions and exception handlers for the application
"""
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException


class ErrorResponse(BaseModel):
    """
    Standard error response model
    """
    status_code: int
    message: str
    details: Optional[Union[List[Dict[str, Any]], Dict[str, Any], str]] = None


class DatabaseError(Exception):
    """Exception raised for database-related errors"""
    def __init__(self, message: str = "Database error occurred"):
        self.message = message
        super().__init__(self.message)


class CacheError(Exception):
    """Exception raised for cache-related errors"""
    def __init__(self, message: str = "Cache error occurred"):
        self.message = message
        super().__init__(self.message)


class TaskQueueError(Exception):
    """Exception raised for task queue related errors"""
    def __init__(self, message: str = "Task queue error occurred"):
        self.message = message
        super().__init__(self.message)


class ResourceNotFoundError(Exception):
    """Exception raised when a resource is not found"""
    def __init__(self, resource_type: str, resource_id: Any):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(self.message)


class BusinessLogicError(Exception):
    """Exception raised for business logic errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers with the FastAPI application
    """
    # Handle validation errors (from Pydantic)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    
    # Handle HTTP exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # Handle SQLAlchemy errors
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    
    # Handle custom exceptions
    app.add_exception_handler(DatabaseError, database_error_handler)
    app.add_exception_handler(CacheError, cache_error_handler)
    app.add_exception_handler(TaskQueueError, task_queue_error_handler)
    app.add_exception_handler(ResourceNotFoundError, resource_not_found_error_handler)
    app.add_exception_handler(BusinessLogicError, business_logic_error_handler)
    
    # Catch-all for any unhandled exceptions
    app.add_exception_handler(Exception, unhandled_exception_handler)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for request validation errors
    """
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            message="Validation error",
            details=exc.errors(),
        ).model_dump(),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler for HTTP exceptions
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status_code=exc.status_code,
            message=str(exc.detail),
        ).model_dump(),
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handler for SQLAlchemy errors
    """
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Database error",
            details=str(exc),
        ).model_dump(),
    )


async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """
    Handler for database errors
    """
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=exc.message,
        ).model_dump(),
    )


async def cache_error_handler(request: Request, exc: CacheError) -> JSONResponse:
    """
    Handler for cache errors
    """
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=exc.message,
        ).model_dump(),
    )


async def task_queue_error_handler(request: Request, exc: TaskQueueError) -> JSONResponse:
    """
    Handler for task queue errors
    """
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=exc.message,
        ).model_dump(),
    )


async def resource_not_found_error_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    """
    Handler for resource not found errors
    """
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content=ErrorResponse(
            status_code=HTTPStatus.NOT_FOUND,
            message=exc.message,
        ).model_dump(),
    )


async def business_logic_error_handler(request: Request, exc: BusinessLogicError) -> JSONResponse:
    """
    Handler for business logic errors
    """
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content=ErrorResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            message=exc.message,
        ).model_dump(),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for all unhandled exceptions
    """
    # Log the exception here before returning response
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Internal server error",
        ).model_dump(),
    )
