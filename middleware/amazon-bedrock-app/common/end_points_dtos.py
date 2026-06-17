from common.base_classes import BaseReqDto, BaseRespDto
from common.models.end_points import EndPointDef


class EndPointReqDto(BaseReqDto):
    endpoint_type: str = "openapi_vector_store"


class EndPointRespDto(BaseRespDto):
    endpoint_instance_ref_id: str = "undefined"
    endpoint_type: str = "openapi_vector_store"
    endpoints_list: list[EndPointDef] = []


class EndPointResp(BaseRespDto):
    status: str = ""
    message: str = ""
    end_point_def: EndPointDef | None = None
    end_point_defs: list[EndPointDef] = []
