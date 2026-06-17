import logging

from common.di import component
from common.end_points_dtos import EndPointReqDto, EndPointRespDto
from common.interfaces.end_points import EndPointsDao
from common.models.end_points import EndPointDef
from configs.end_points_master import END_POINTS_MASTER

LOGGER = logging.getLogger(__name__)

VECTOR_STORE = "vector_store"


@component(key=EndPointsDao.__name__)
class EndPointsDaoImpl(EndPointsDao):

    def create_end_point(self, end_point_data: EndPointReqDto, resp: EndPointRespDto):
        pass

    def get_end_point(self, end_point_data: EndPointReqDto, resp: EndPointRespDto):
        pass

    def get_end_points_list(self, end_point_data: EndPointReqDto, resp: EndPointRespDto):
        # Return the end point names from the internal master catalog. The
        # object_id stays internal and is not exposed to the API.
        resp.endpoints_list = [
            EndPointDef(name=entry.name, end_point_type=VECTOR_STORE)
            for entry in END_POINTS_MASTER
        ]
        return resp
