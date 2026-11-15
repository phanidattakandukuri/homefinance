import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def error_payload(message: str, details: Any = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": {"message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.info("Request validation failed: %s %s", request.method, request.url.path)
    return JSONResponse(status_code=422, content=error_payload("Request validation failed", exc.errors()))
