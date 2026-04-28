from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# ── Custom Exceptions ──────────────────────────────────────────────

class LuminaryException(Exception):
    """Base exception for all Luminary errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DocumentNotFound(LuminaryException):
    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document with id '{document_id}' was not found.",
            status_code=404
        )


class InvalidToken(LuminaryException):
    def __init__(self):
        super().__init__(
            message="Invalid or expired token.",
            status_code=401
        )


class UnauthorizedAccess(LuminaryException):
    def __init__(self):
        super().__init__(
            message="You do not have permission to access this resource.",
            status_code=403
        )


class DocumentProcessingError(LuminaryException):
    def __init__(self, filename: str):
        super().__init__(
            message=f"Failed to process document '{filename}'.",
            status_code=422
        )


class UserAlreadyExists(LuminaryException):
    def __init__(self, email: str):
        super().__init__(
            message=f"User with email '{email}' already exists.",
            status_code=409
        )


# ── Register Handlers ──────────────────────────────────────────────

def register_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""

    @app.exception_handler(LuminaryException)
    async def luminary_exception_handler(
        request: Request,
        exc: LuminaryException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": type(exc).__name__,
                "message": exc.message,
                "status_code": exc.status_code,
            }
        )