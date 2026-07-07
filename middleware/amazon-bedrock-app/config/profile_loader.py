"""Load and deep-merge layered application YAML profiles."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

_CONFIG_DIR = Path(__file__).resolve().parent

_PROFILE_FILE_ALIASES: dict[str, str] = {
    "local": "local",
    "docker": "docker",
    "prod": "prod",
    "production": "prod",
}


def resolve_profile_name(profile: str | None = None) -> str:
    """Return the normalized profile file suffix (local, docker, prod)."""
    raw = (profile or os.environ.get("APP_PROFILE", "local")).strip().lower()
    normalized = _PROFILE_FILE_ALIASES.get(raw)
    if normalized is None:
        raise ValueError(
            f"Unknown APP_PROFILE '{raw}'. Expected one of: "
            f"{', '.join(sorted(_PROFILE_FILE_ALIASES))}"
        )
    return normalized


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge *override* into a copy of *base*."""
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def load_profile_config(profile: str | None = None) -> dict[str, Any]:
    """Deep-merge ``application.yaml`` with ``application-{profile}.yaml``."""
    profile_name = resolve_profile_name(profile)
    base = _load_yaml(_CONFIG_DIR / "application.yaml")
    profile_data = _load_yaml(_CONFIG_DIR / f"application-{profile_name}.yaml")
    return deep_merge(base, profile_data)


def apply_secret_env_overrides(config: dict[str, Any]) -> dict[str, Any]:
    """Apply explicit environment-variable overrides for secrets only."""
    from config.secret_env import apply_secret_overrides

    return apply_secret_overrides(config)
