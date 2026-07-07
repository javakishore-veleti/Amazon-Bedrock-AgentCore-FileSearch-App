from dataclasses import dataclass

from config.app_settings import AppSettings


@dataclass(frozen=True)
class ObservabilitySettings:
    """Feature toggles and config for logging / OpenTelemetry."""

    otel_enabled: bool = False
    log_level: str = "INFO"
    log_json: bool = False
    otel_service_name: str = "filesearch-api"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"

    @classmethod
    def from_app_settings(cls, app_settings: AppSettings) -> "ObservabilitySettings":
        obs = app_settings.observability
        return cls(
            otel_enabled=obs.otel_enabled,
            log_level=obs.log_level.upper(),
            log_json=obs.log_json,
            otel_service_name=obs.otel_service_name,
            otel_exporter_otlp_endpoint=obs.otel_exporter_otlp_endpoint,
        )
