import logging
from typing import Any

from common.di import component
from common.interfaces.app_cache import AppCacheSvc

LOGGER = logging.getLogger(__name__)


@component(key=AppCacheSvc.__name__)
class AppCacheSvcImpl(AppCacheSvc):
    def __init__(self):
        # cache_type -> { key -> value }
        self._cache: dict[str, dict[str, Any]] = {}

    def put(self, cache_type: str, key: str, value: Any):
        self._cache.setdefault(cache_type, {})[key] = value

    def get(self, cache_type: str, key: str) -> Any:
        return self._cache.get(cache_type, {}).get(key)

    def get_all(self, cache_type: str) -> dict:
        return dict(self._cache.get(cache_type, {}))

    def has(self, cache_type: str, key: str) -> bool:
        return key in self._cache.get(cache_type, {})
