import logging

from common.observability.settings import ObservabilitySettings

LOGGER = logging.getLogger(__name__)
_otel_configured = False


def configure_otel(settings: ObservabilitySettings) -> None:
    """Initialize OpenTelemetry only when OTEL_ENABLED=true (default false)."""
    global _otel_configured
    if not settings.otel_enabled:
        LOGGER.info("OpenTelemetry disabled (OTEL_ENABLED=false)")
        return
    if _otel_configured:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError as exc:
        LOGGER.warning(
            "OTEL_ENABLED=true but OpenTelemetry packages are not installed: %s. "
            "Install optional deps from requirements-otel.txt",
            exc,
        )
        return

    resource = Resource.create({"service.name": settings.otel_service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    _otel_configured = True
    LOGGER.info(
        "OpenTelemetry enabled service=%s endpoint=%s",
        settings.otel_service_name,
        settings.otel_exporter_otlp_endpoint,
    )


def is_otel_enabled() -> bool:
    return _otel_configured
