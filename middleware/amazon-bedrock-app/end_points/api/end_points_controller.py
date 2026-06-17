import logging

from fastapi import APIRouter, Depends

from common.end_points_dtos import EndPointReqDto, EndPointRespDto, EndPointResp
from common.interfaces.end_points import EndPointService
from end_points.service.end_points_svc_provider import get_end_point_service

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/api/end_points", tags=["end_points"])


@router.get("/list", response_model=EndPointResp)
async def list_end_points(
    end_point_service: EndPointService = Depends(get_end_point_service),
):
    """List available end points for searching"""
    end_point_req = EndPointReqDto()
    end_point_resp_dto = EndPointRespDto()

    try:
        end_point_service.get_end_points_list(end_point_req, end_point_resp_dto)
    except Exception as exc:
        LOGGER.error("Failed to list end points: %s", exc)

    # Map the internal service DTO to the API response, echoing the request id.
    return EndPointResp(
        request_id=end_point_req.request_id,
        end_point_defs=end_point_resp_dto.endpoints_list,
    )
