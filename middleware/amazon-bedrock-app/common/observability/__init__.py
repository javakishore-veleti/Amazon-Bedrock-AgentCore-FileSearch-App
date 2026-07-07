"""Observability bootstrap: logging (always) and OTEL (feature-toggled, default off)."""

from config.app_settings import AppSettings

from common.observability.logging_config import configure_logging
from common.observability.otel_setup import configure_otel
from common.observability.settings import ObservabilitySettings


def configure_observability(app_settings: AppSettings) -> ObservabilitySettings:
    """Configure logging and optionally OpenTelemetry. Call once at app startup."""
    settings = ObservabilitySettings.from_app_settings(app_settings)
    configure_logging(settings)
    configure_otel(settings)
    return settings
