"""Decorator-based dependency injection on top of ObjectsFactory.

Annotate a class with ``@component(key=..., depends_on=[...])`` to declare its
registration key and the keys it depends on. At startup ``wire_components()``
instantiates every annotated component in dependency order, injecting the
already-built dependencies (positionally, in ``depends_on`` order) and
registering each instance into the ObjectsFactory under its key.
"""

import logging

from common.objects_factory import ObjectsFactory

LOGGER = logging.getLogger(__name__)


class ComponentSpec:
    def __init__(self, cls, key: str, depends_on: list[str]):
        self.cls = cls
        self.key = key
        self.depends_on = depends_on


# Populated by the @component decorator at import time.
_COMPONENTS: list[ComponentSpec] = []


def component(key: str, depends_on: list[str] | None = None):
    """Class decorator declaring a DI component, its key, and its dependencies."""

    def decorator(cls):
        deps = list(depends_on or [])
        _COMPONENTS.append(ComponentSpec(cls, key, deps))
        cls.__di_key__ = key
        cls.__di_depends_on__ = deps
        return cls

    return decorator


def _ordered_specs() -> list[ComponentSpec]:
    """Topologically sort components so dependencies come before dependents."""
    by_key = {spec.key: spec for spec in _COMPONENTS}
    resolved: set[str] = set()
    order: list[ComponentSpec] = []

    def visit(spec: ComponentSpec, visiting: set[str]):
        if spec.key in resolved:
            return
        if spec.key in visiting:
            raise ValueError(f"Circular dependency detected at '{spec.key}'")
        visiting.add(spec.key)
        for dep_key in spec.depends_on:
            dep_spec = by_key.get(dep_key)
            if dep_spec is None:
                raise KeyError(
                    f"Component '{spec.key}' depends on unknown key '{dep_key}'"
                )
            visit(dep_spec, visiting)
        visiting.discard(spec.key)
        resolved.add(spec.key)
        order.append(spec)

    for spec in _COMPONENTS:
        visit(spec, set())
    return order


def wire_components(factory: ObjectsFactory) -> int:
    """Instantiate every annotated component in dependency order and register it.

    Each component is built with its dependencies passed positionally in the
    order given by ``depends_on``. Returns the number of components wired.
    """
    order = _ordered_specs()
    for spec in order:
        deps = [factory.get(dep_key) for dep_key in spec.depends_on]
        instance = spec.cls(*deps)
        factory.register(spec.key, instance)
        LOGGER.info("Wired %s as %s", spec.cls.__name__, spec.key)
    return len(order)
