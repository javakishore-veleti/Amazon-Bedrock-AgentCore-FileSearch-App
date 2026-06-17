import logging

from fastapi import APIRouter, Depends

from common.end_points_dtos import EndPointResp
from common.interfaces.end_points import EndPointService
from end_points.service.end_points_svc_provider import get_end_point_service

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/api/end_points", tags=["end_points"])


@router.get("/list", response_model=EndPointResp)
async def list_end_points(
    end_point_service: EndPointService = Depends(get_end_point_service),
):
    """List available end points for searching"""
    end_point_resp = EndPointResp()

    try:
        end_point_service.get_end_points_list(None, end_point_resp)
        end_point_resp.end_point_defs = []
    except Exception as exc:
        LOGGER.error("Failed to list end points: %s", exc)

    return end_point_resp
