from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("NOT_FOUND", message, status_code=404, details=details)


class ConflictError(AppError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__("CONFLICT", message, status_code=409, details=details)


def error_payload(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "result": None,
        "source_refs": [],
        "system": "unknown",
        "session_id": None,
        "warnings": [],
        "error": {"code": code, "message": message, "details": details or {}},
    }


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return str(value)



COMPAT_SYSTEMS = {
    "/api/session/event": "session-event-v1",
    "/api/user/notes": "user-notes-v1",
}


def _compat_error_payload(
    system: str,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from app.schemas.compat import compat_failure

    return compat_failure(
        system=system,
        code=code,
        message=message,
        details=details,
    ).model_dump(mode="json")

def sanitize_validation_errors(errors: Sequence[Any]) -> list[dict[str, Any]]:
    return [
        {
            "type": error.get("type", "validation_error"),
            "location": [str(part) for part in error.get("loc", [])],
            "message": error.get("msg", "Invalid value"),
        }
        for error in errors
    ]


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        compat_system = COMPAT_SYSTEMS.get(request.url.path)
        content = (
            _compat_error_payload(compat_system, exc.code, exc.message, exc.details)
            if compat_system
            else error_payload(exc.code, exc.message, exc.details)
        )
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = {"errors": sanitize_validation_errors(exc.errors())}
        compat_system = COMPAT_SYSTEMS.get(request.url.path)
        if compat_system:
            return JSONResponse(
                status_code=400,
                content=_compat_error_payload(
                    compat_system,
                    "VALIDATION_ERROR",
                    "Request validation failed",
                    details,
                ),
            )
        return JSONResponse(
            status_code=422,
            content=error_payload("VALIDATION_ERROR", "Request validation failed", details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        compat_system = COMPAT_SYSTEMS.get(request.url.path)
        content = (
            _compat_error_payload(compat_system, "HTTP_ERROR", str(exc.detail))
            if compat_system
            else error_payload("HTTP_ERROR", str(exc.detail))
        )
        return JSONResponse(status_code=exc.status_code, content=content)
