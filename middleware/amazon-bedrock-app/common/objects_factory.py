"""A tiny registry of named singleton objects.

Acts as a minimal composition container: register an object once under a
string key, then fetch it anywhere. Registering a key that already exists is
an error, so a singleton can never be silently replaced.
"""

from typing import Any


class ObjectsFactory:
    def __init__(self):
        self._objects: dict[str, Any] = {}

    def register(self, key: str, obj: Any) -> Any:
        """Register ``obj`` under ``key``. Raises if the key already exists."""
        if key in self._objects:
            raise ValueError(f"Object with key '{key}' is already registered")
        self._objects[key] = obj
        return obj

    def get(self, key: str) -> Any:
        """Return the object registered under ``key``. Raises if missing."""
        if key not in self._objects:
            raise KeyError(f"No object registered under key '{key}'")
        return self._objects[key]

    def has(self, key: str) -> bool:
        """Return True if ``key`` is registered."""
        return key in self._objects


# Process-wide singleton factory.
OBJECTS_FACTORY = ObjectsFactory()
