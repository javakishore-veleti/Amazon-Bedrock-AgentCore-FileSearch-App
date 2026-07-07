"""Immutable application settings singleton loaded from layered YAML profiles."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from config.profile_loader import apply_secret_env_overrides, load_profile_config, resolve_profile_name

LOGGER = logging.getLogger(__name__)

_settings: AppSettings | None = None


class AppRuntimeConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    debug: bool = False
    python_port: int = 8000
    log_level: str = "INFO"


class ObservabilityConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    otel_enabled: bool = False
    log_level: str = "INFO"
    log_json: bool = False
    otel_service_name: str = "filesearch-api"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"


class AwsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    region: str = "us-east-1"
    access_key_id: str = ""
    secret_access_key: str = ""


class BedrockConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    model_id: str = "anthropic.claude-v2"
    agent_alias_id: str = ""


class DatabaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str = ""


class OpenAIVectorStoreConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    api_key: str = ""
    org_id: str = ""
    base_url: str = "https://api.openai.com/v1"
    vector_store_id: str = ""


class PgVectorConfig(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    db_schema: str = Field(default="ingest_ops", validation_alias="schema")
    table: str = "document_embeddings"
    embedding_dimension: int = 384
    embedding_model: str = "all-MiniLM-L6-v2"
    password: str = ""


class VectorStoreConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider: str = "pgvector"
    openai: OpenAIVectorStoreConfig = Field(default_factory=OpenAIVectorStoreConfig)
    pgvector: PgVectorConfig = Field(default_factory=PgVectorConfig)


class FileSearchConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    max_file_size_mb: int = 100
    supported_file_types: str = ".pdf,.txt,.json,.csv,.docx"


class AppSettings(BaseModel):
    """Frozen settings loaded once at startup from YAML profiles."""

    model_config = ConfigDict(frozen=True)

    profile: str = "local"
    app: AppRuntimeConfig = Field(default_factory=AppRuntimeConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    aws: AwsConfig = Field(default_factory=AwsConfig)
    bedrock: BedrockConfig = Field(default_factory=BedrockConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    file_search: FileSearchConfig = Field(default_factory=FileSearchConfig)
    book_ingest: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_profile(cls, profile: str | None = None) -> AppSettings:
        profile_name = resolve_profile_name(profile)
        raw = load_profile_config(profile)
        raw = apply_secret_env_overrides(raw)
        raw["profile"] = profile_name
        return cls.model_validate(raw)


def load_app_settings(profile: str | None = None) -> AppSettings:
    """Load settings once; subsequent calls return the same instance."""
    global _settings
    if _settings is not None:
        return _settings
    _settings = AppSettings.from_profile(profile)
    LOGGER.info("Loaded application profile '%s'", _settings.profile)
    return _settings


def get_app_settings() -> AppSettings:
    """Return the loaded settings singleton."""
    if _settings is None:
        raise RuntimeError("AppSettings not loaded; call load_app_settings() at startup")
    return _settings
