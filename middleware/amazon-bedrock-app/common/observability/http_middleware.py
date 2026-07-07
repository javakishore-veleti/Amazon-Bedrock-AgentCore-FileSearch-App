import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from common.observability.logging_config import request_id_ctx
from common.observability.span_helper import traced_span

LOGGER = logging.getLogger(__name__)
REQUEST_ID_HEADER = "X-Request-Id"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Bind request_id for logs/spans; emit API entry/exit logs."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        token = request_id_ctx.set(request_id)
        path = request.url.path
        started = time.monotonic()
        attrs = {
            "app.request_id": request_id,
            "http.method": request.method,
            "http.route": path,
        }
        LOGGER.info(
            "Entering api request_id=%s method=%s path=%s",
            request_id,
            request.method,
            path,
        )
        try:
            with traced_span(f"api {request.method} {path}", attributes=attrs):
                response = await call_next(request)
            duration_ms = int((time.monotonic() - started) * 1000)
            LOGGER.info(
                "Exiting api request_id=%s method=%s path=%s status=%d duration_ms=%d",
                request_id,
                request.method,
                path,
                response.status_code,
                duration_ms,
            )
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        except Exception:
            duration_ms = int((time.monotonic() - started) * 1000)
            LOGGER.exception(
                "Exiting api request_id=%s method=%s path=%s duration_ms=%d error=true",
                request_id,
                request.method,
                path,
                duration_ms,
            )
            raise
        finally:
            request_id_ctx.reset(token)
