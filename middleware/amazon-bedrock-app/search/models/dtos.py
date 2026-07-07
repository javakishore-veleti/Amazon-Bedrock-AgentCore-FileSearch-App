from pydantic import Field

from common.base_classes import BaseReqDto, BaseRespDto
from common.dtos import SearchHit


class SearchReq(BaseReqDto):
    """API request body for POST /api/search."""

    query: str
    vector_store_name: str = ""
    top_k: int = Field(default=5, ge=1, le=50)
    ebook_id: str = ""
    author: str = ""


class SearchResp(BaseRespDto):
    """API response for POST /api/search."""

    query: str = ""
    vector_store_name: str = ""
    hits: list[SearchHit] = Field(default_factory=list)
    message: str = ""
