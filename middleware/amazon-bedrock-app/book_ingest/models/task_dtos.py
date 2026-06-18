from typing import Optional

from common.base_classes import BaseReqDto, BaseRespDto


class BookIngestTaskReq(BaseReqDto):
    """Shared ingestion context passed into every task (no loose args)."""

    manifest_id: int = 0
    target_id: int = 0
    ebook_id: str = ""
    title: str = ""
    author: Optional[str] = None
    source_url: str = ""
    txt_url: str = ""
    vector_store_name: str = ""
    vector_store_id: str = ""

    raw_text: Optional[str] = None
    raw_path: Optional[str] = None
    clean_text: Optional[str] = None
    processed_path: Optional[str] = None
    sections: list = []
    source_hash: Optional[str] = None
    metadata: dict = {}
    duplicate: bool = False
    provider_file_id: Optional[str] = None
    status: Optional[str] = None
    terminal: bool = False
    attempt: int = 0


class BookIngestTaskResp(BaseRespDto):
    """Partial updates a task contributes back to the context."""

    raw_text: Optional[str] = None
    raw_path: Optional[str] = None
    clean_text: Optional[str] = None
    processed_path: Optional[str] = None
    sections: Optional[list] = None
    source_hash: Optional[str] = None
    metadata: Optional[dict] = None
    duplicate: Optional[bool] = None
    provider_file_id: Optional[str] = None
    status: Optional[str] = None
    terminal: Optional[bool] = None
    route: Optional[str] = None
    error: Optional[str] = None

    def merge_dict(self) -> dict:
        """Fields actually set by the task (for merging into the context)."""
        return self.model_dump(exclude_none=True, exclude={"request_id", "route"})
