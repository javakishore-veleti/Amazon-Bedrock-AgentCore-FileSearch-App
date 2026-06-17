"""Application bootstrap / composition root.

Called once at startup. Importing the component modules below runs their
``@component`` decorators, which declare each class's DI key and dependencies.
``wire_components`` then instantiates them in dependency order and registers
each into the shared ObjectsFactory.
"""

import logging

from common.di import wire_components
from common.objects_factory import OBJECTS_FACTORY

# Import component modules so their @component decorators register the classes.
# Add new DAO/service modules here for them to be wired at startup.
import end_points.dao.end_points_dao  # noqa: F401
import end_points.service.end_points_svc  # noqa: F401

LOGGER = logging.getLogger(__name__)


def register_services():
    """Wire every annotated component into the ObjectsFactory."""
    count = wire_components(OBJECTS_FACTORY)
    LOGGER.info("Registered %d component(s)", count)
