from typing import Any


class AppCacheSvc:
    """In-memory cache namespaced by a cache type."""

    def put(self, cache_type: str, key: str, value: Any):
        raise NotImplementedError("This method should be implemented by subclasses")

    def get(self, cache_type: str, key: str) -> Any:
        raise NotImplementedError("This method should be implemented by subclasses")

    def get_all(self, cache_type: str) -> dict:
        raise NotImplementedError("This method should be implemented by subclasses")

    def has(self, cache_type: str, key: str) -> bool:
        raise NotImplementedError("This method should be implemented by subclasses")
