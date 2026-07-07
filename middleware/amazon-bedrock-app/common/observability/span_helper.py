import logging
from contextlib import contextmanager
from typing import Any, Iterator

from common.observability.logging_config import request_id_ctx
from common.observability.otel_setup import is_otel_enabled

LOGGER = logging.getLogger(__name__)


class _NullSpan:
    def set_attribute(self, key: str, value: Any) -> None:
        return None

    def record_exception(self, exc: BaseException) -> None:
        return None


@contextmanager
def traced_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[Any]:
    """Start an OTEL span when enabled; otherwise a no-op span (zero export cost)."""
    attrs = dict(attributes or {})
    rid = request_id_ctx.get()
    if rid:
        attrs.setdefault("app.request_id", rid)

    if not is_otel_enabled():
        yield _NullSpan()
        return

    from opentelemetry import trace

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(name, attributes=attrs) as span:
        yield span
