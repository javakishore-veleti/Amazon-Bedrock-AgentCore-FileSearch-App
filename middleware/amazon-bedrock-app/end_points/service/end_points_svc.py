import logging

from common.end_points_dtos import  EndPointReqDto, EndPointRespDto
from common.interfaces.end_points import EndPointService, EndPointsDao
from common.objects_factory import ObjectsFactory

LOGGER = logging.getLogger(__name__)

class EndPointsServiceImpl(EndPointService):
    def __init__(self, end_points_dao: EndPointsDao):
        self.end_points_dao = end_points_dao

    @classmethod
    def register(cls, factory: ObjectsFactory):
        """Register a singleton of this service under the interface name.

        Resolves the EndPointsDao (registered earlier) from the factory and
        injects it, so the service holds a ref to the DAO interface impl.
        """
        end_points_dao = factory.get(EndPointsDao.__name__)
        factory.register(EndPointService.__name__, cls(end_points_dao=end_points_dao))
        LOGGER.info("Registered %s as %s", cls.__name__, EndPointService.__name__)

    def create_end_point(self, end_point_data:EndPointReqDto, resp:EndPointRespDto):
        return self.end_points_dao.create_end_point(end_point_data, resp)

    def get_end_point(self, end_point_data:EndPointReqDto, resp:EndPointRespDto):
        return self.end_points_dao.get_end_point(end_point_data, resp)

    def get_end_points_list(self, end_point_data:EndPointReqDto, resp:EndPointRespDto):
        return self.end_points_dao.get_end_points_list(end_point_data, resp)
