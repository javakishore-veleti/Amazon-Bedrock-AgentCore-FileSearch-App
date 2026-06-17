import logging

from common.di import component
from common.end_points_dtos import  EndPointReqDto, EndPointRespDto
from common.interfaces.end_points import EndPointService, EndPointsDao

LOGGER = logging.getLogger(__name__)


@component(key=EndPointService.__name__, depends_on=[EndPointsDao.__name__])
class EndPointsServiceImpl(EndPointService):
    def __init__(self, end_points_dao: EndPointsDao):
        self.end_points_dao = end_points_dao

    def create_end_point(self, end_point_data:EndPointReqDto, resp:EndPointRespDto):
        return self.end_points_dao.create_end_point(end_point_data, resp)

    def get_end_point(self, end_point_data:EndPointReqDto, resp:EndPointRespDto):
        return self.end_points_dao.get_end_point(end_point_data, resp)

    def get_end_points_list(self, end_point_data:EndPointReqDto, resp:EndPointRespDto):
        return self.end_points_dao.get_end_points_list(end_point_data, resp)
