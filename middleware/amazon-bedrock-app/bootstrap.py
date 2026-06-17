"""Application bootstrap / composition root.

Called once at startup. Importing the component modules below runs their
``@component`` decorators, which declare each class's DI key and dependencies.
``wire_components`` then instantiates them in dependency order and registers
each into the shared ObjectsFactory. Finally caches are warmed.
"""

import logging

from common.di import wire_components
from common.end_points_dtos import EndPointRespDto
from common.interfaces.app_cache import AppCacheSvc
from common.interfaces.end_points import EndPointsDao
from common.objects_factory import OBJECTS_FACTORY
from configs.end_points_master import END_POINTS_BY_NAME

# Import component modules so their @component decorators register the classes.
# Add new DAO/service/facade modules here for them to be wired at startup.
import common.caching.service.app_cache_svc  # noqa: F401
import end_points.dao.end_points_dao  # noqa: F401
import end_points.service.end_points_svc  # noqa: F401
import vector_store.openai_ingest_facade  # noqa: F401
import vector_store.service.ingest_svc  # noqa: F401

LOGGER = logging.getLogger(__name__)


def register_services():
    """Wire every annotated component into the ObjectsFactory, then warm caches."""
    count = wire_components(OBJECTS_FACTORY)
    LOGGER.info("Registered %d component(s)", count)
    _warm_vector_store_cache()


def _warm_vector_store_cache():
    """Cache the DAO's vector store list as name -> object_id, by store type."""
    cache = OBJECTS_FACTORY.get(AppCacheSvc.__name__)
    dao = OBJECTS_FACTORY.get(EndPointsDao.__name__)

    resp = EndPointRespDto()
    dao.get_end_points_list(None, resp)

    cached = 0
    for end_point in resp.endpoints_list:
        object_id = END_POINTS_BY_NAME.get(end_point.name)
        if object_id:
            cache.put(end_point.end_point_type, end_point.name, object_id)
            cached += 1
    LOGGER.info("Warmed cache with %d vector store entries", cached)
