"""Provider that resolves the EndPointService dependency.

The concrete implementation registers itself into the ObjectsFactory at startup
(see bootstrap.py). This provider only looks it up by interface name, so neither
it nor the controller ever imports the Impl class.
"""

from common.interfaces.end_points import EndPointService
from common.objects_factory import OBJECTS_FACTORY


def get_end_point_service() -> EndPointService:
    """Return the singleton ``EndPointService`` registered at startup."""
    return OBJECTS_FACTORY.get(EndPointService.__name__)
