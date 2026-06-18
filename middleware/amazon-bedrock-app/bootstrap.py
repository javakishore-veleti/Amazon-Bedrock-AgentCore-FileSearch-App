"""Application bootstrap / composition root.

Called once at startup. Importing the component modules below runs their
``@component`` decorators, which declare each class's DI key and dependencies.
``wire_components`` then instantiates them in dependency order and registers
each into the shared ObjectsFactory. Finally caches are warmed.
"""

import logging

from common.di import wire_components
from common.interfaces.app_cache import AppCacheSvc
from common.objects_factory import OBJECTS_FACTORY
from configs.end_points_master import END_POINTS_MASTER, VECTOR_STORE_TYPE

# Import component modules so their @component decorators register the classes.
# Add new DAO/service/facade modules here for them to be wired at startup.
import common.caching.service.app_cache_svc  # noqa: F401
import end_points.dao.end_points_dao  # noqa: F401
import end_points.service.end_points_svc  # noqa: F401
import vector_store.adapters.openai_ingest_facade  # noqa: F401
import book_ingest.wiring  # noqa: F401  (registers all book_ingest components)

LOGGER = logging.getLogger(__name__)


def register_services():
    """Wire every annotated component into the ObjectsFactory, then warm caches."""
    count = wire_components(OBJECTS_FACTORY)
    LOGGER.info("Registered %d component(s)", count)
    _warm_vector_store_cache()


def _warm_vector_store_cache():
    """Cache the vector store catalog as name -> object_id, keyed by store type."""
    cache = OBJECTS_FACTORY.get(AppCacheSvc.__name__)
    for entry in END_POINTS_MASTER:
        cache.put(VECTOR_STORE_TYPE, entry.name, entry.object_id)
    LOGGER.info("Warmed cache with %d vector store entries", len(END_POINTS_MASTER))
