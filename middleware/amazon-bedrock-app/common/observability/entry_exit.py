import logging
import time
from functools import wraps
from typing import Any, Callable, TypeVar

from common.observability.logging_config import request_id_ctx
from common.observability.span_helper import traced_span

LOGGER = logging.getLogger(__name__)
F = TypeVar("F", bound=Callable[..., Any])


def log_enter_exit(
    *,
    span_name: str | None = None,
    concept: str = "",
    extra_attrs: dict[str, Any] | None = None,
) -> Callable[[F], F]:
    """Decorator: entry/exit logs + optional OTEL span (no-op when OTEL disabled)."""

    def decorator(fn: F) -> F:
        qualified = span_name or fn.__qualname__

        @wraps(fn)
        def wrapper(*args, **kwargs):
            rid = request_id_ctx.get() or "-"
            attrs = dict(extra_attrs or {})
            if concept:
                attrs["app.concept"] = concept
            attrs["app.request_id"] = rid
            started = time.monotonic()
            LOGGER.info("Entering %s request_id=%s", qualified, rid)
            with traced_span(qualified, attributes=attrs):
                try:
                    result = fn(*args, **kwargs)
                    duration_ms = int((time.monotonic() - started) * 1000)
                    LOGGER.info(
                        "Exiting %s request_id=%s duration_ms=%d",
                        qualified,
                        rid,
                        duration_ms,
                    )
                    return result
                except Exception:
                    duration_ms = int((time.monotonic() - started) * 1000)
                    LOGGER.exception(
                        "Exiting %s request_id=%s duration_ms=%d error=true",
                        qualified,
                        rid,
                        duration_ms,
                    )
                    raise

        return wrapper  # type: ignore[return-value]

    return decorator
