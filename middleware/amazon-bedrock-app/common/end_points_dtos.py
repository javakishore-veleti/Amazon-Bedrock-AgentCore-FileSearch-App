from pydantic import BaseModel

from common.models.end_points import EndPointDef


class EndPointReqDto:
    def __init__(self, endpoint_id: str):
        self.endpoint_type: str = "openapi_vector_store"


class EndPointRespDto:
    def __init__(self, endpoint_id: str):
        self.endpoint_instance_ref_id: str = "undefined"
        self.endpoint_type: str = "openapi_vector_store"
        self.endpoints_list: list[EndPointDef] = []


class EndPointResp(BaseModel):
    status: str = ""
    message: str = ""
    end_point_def: EndPointDef | None = None
    end_point_defs: list[EndPointDef] = []
