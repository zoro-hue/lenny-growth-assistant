from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.error_code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


AppError = AppException


class EntityNotFoundError(AppException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            message=f"{entity_name} with id '{entity_id}' was not found.",
            code="ENTITY_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"entity": entity_name, "id": entity_id},
        )


class DatabaseConnectionError(AppException):
    def __init__(self, message: str = "Database connection failed or unavailable."):
        super().__init__(
            message=message,
            code="DB_CONNECTION_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class BadRequestError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="BAD_REQUEST",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


def format_error_response(code: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning(f"AppException: {exc.code} - {exc.message} on {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(exc.code, exc.message, exc.details),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    formatted_errors = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", [])])
        formatted_errors.append({
            "field": field,
            "message": err.get("msg", ""),
            "type": err.get("type", ""),
        })

    status_422 = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", status.HTTP_422_UNPROCESSABLE_ENTITY)
    return JSONResponse(
        status_code=status_422,
        content=format_error_response(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            details={"errors": formatted_errors},
        ),
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.error(f"SQLAlchemyError on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=format_error_response(
            code="DATABASE_ERROR",
            message="Database query or connection operation failed.",
            details={"type": exc.__class__.__name__},
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled server error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected internal server error occurred.",
        ),
    )
