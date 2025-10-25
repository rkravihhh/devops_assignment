"""
Custom exception handlers for the application.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog

logger = structlog.get_logger()


class TxnReconcileException(Exception):
    """Base exception for the application."""
    pass


class TransactionNotFoundError(TxnReconcileException):
    """Raised when a transaction is not found."""
    pass


class ReconciliationError(TxnReconcileException):
    """Raised when reconciliation fails."""
    pass


class IssuerNotFoundError(TxnReconcileException):
    """Raised when an issuer is not found."""
    pass


class ValidationError(TxnReconcileException):
    """Raised when data validation fails."""
    pass


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions."""
    logger.warning(
        "Validation error",
        errors=exc.errors(),
        path=request.url.path
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )


async def mock_database_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle mock database exceptions."""
    logger.error(
        "Mock database error",
        error=str(exc),
        path=request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database Error",
            "message": "An internal database error occurred"
        }
    )


async def txn_reconcile_exception_handler(request: Request, exc: TxnReconcileException) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.warning(
        "Application error",
        error=str(exc),
        path=request.url.path
    )
    return JSONResponse(
        status_code=400,
        content={
            "error": "Application Error",
            "message": str(exc)
        }
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup all exception handlers."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, mock_database_exception_handler)
    app.add_exception_handler(TxnReconcileException, txn_reconcile_exception_handler)
