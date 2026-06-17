import logging

from common.end_points_dtos import EndPointReqDto, EndPointRespDto
from common.interfaces.end_points import EndPointsDao
from common.objects_factory import ObjectsFactory

LOGGER = logging.getLogger(__name__)


class EndPointsDaoImpl(EndPointsDao):

    @classmethod
    def register(cls, factory: ObjectsFactory):
        """Register a singleton of this DAO under the interface name."""
        factory.register(EndPointsDao.__name__, cls())
        LOGGER.info("Registered %s as %s", cls.__name__, EndPointsDao.__name__)

    def create_end_point(self, end_point_data: EndPointReqDto, resp: EndPointRespDto):
        pass

    def get_end_point(self, end_point_data: EndPointReqDto, resp: EndPointRespDto):
        pass

    def get_end_points_list(self, end_point_data: EndPointReqDto, resp: EndPointRespDto):
        pass
