"""Application bootstrap / composition root.

Called once at startup. Every service implementation registers itself into the
shared ObjectsFactory here, so the rest of the app resolves services by their
interface name without ever importing a concrete Impl.
"""

import logging

from common.objects_factory import OBJECTS_FACTORY
from end_points.dao.end_points_dao import EndPointsDaoImpl
from end_points.service.end_points_svc import EndPointsServiceImpl

LOGGER = logging.getLogger(__name__)

# DAOs register first because services resolve their DAO at registration time.
DAO_IMPLS = [
    EndPointsDaoImpl,
]

# Every service Impl that should self-register at startup. Add new ones here.
SERVICE_IMPLS = [
    EndPointsServiceImpl,
]


def register_services():
    """Have every DAO and service implementation register itself (DAOs first)."""
    for impl_cls in DAO_IMPLS:
        impl_cls.register(OBJECTS_FACTORY)
    for impl_cls in SERVICE_IMPLS:
        impl_cls.register(OBJECTS_FACTORY)
    LOGGER.info(
        "Registered %d DAO(s) and %d service(s)", len(DAO_IMPLS), len(SERVICE_IMPLS)
    )
