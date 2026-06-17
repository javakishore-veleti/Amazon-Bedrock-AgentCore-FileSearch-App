"""Base DTO classes shared by every request/response DTO.

Every request DTO subclasses ``BaseReqDto`` and every response DTO subclasses
``BaseRespDto``, so they all carry a ``request_id`` used to correlate a response
with its originating request.
"""

import uuid

from pydantic import BaseModel, Field


class BaseReqDto(BaseModel):
    # Auto-generated per request so callers never set it by hand.
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class BaseRespDto(BaseModel):
    request_id: str = ""
