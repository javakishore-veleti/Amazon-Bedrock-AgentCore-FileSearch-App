from typing import Optional

from common.base_classes import BaseReqDto, BaseRespDto


# ---- Async jobs ----
class JobAcceptedResp(BaseRespDto):
    job_id: str = ""
    job_type: str = ""
    status: str = "running"
    status_url: str = ""
    message: str = ""


class RunAllReq(BaseReqDto):
    """One-click full pipeline: dataset build -> manifest -> ingest."""

    target_count: int = 1000
    vector_stores: list[str] = []
    consumer_count: int = 5
    limit: int = 1000
    overwrite: bool = True


class JobStatusResp(BaseRespDto):
    job_id: str = ""
    job_type: str = ""
    status: str = ""
    result: Optional[dict] = None
    error: Optional[str] = None
    picked_up: Optional[bool] = None
    picked_up_by_id: Optional[int] = None


# ---- Dataset builder ----
class DatasetBuildReq(BaseReqDto):
    source_url: str = "https://www.gutenberg.org/browse/scores/top"
    target_count: int = 1000
    batch_size: int = 1000
    output_dir: str = "DataSets/Novels/BatchFiles"
    source: str = "PROJECT_GUTENBERG_TOP_100_YESTERDAY"
    overwrite: bool = False


class DatasetBuildResp(BaseRespDto):
    status: str = ""
    source_url: str = ""
    books_discovered: int = 0
    books_written: int = 0
    batch_files_created: list[str] = []
    message: str = ""


# ---- Manifest build ----
class ManifestBuildReq(BaseReqDto):
    input_dir: str = "DataSets/Novels/BatchFiles"
    source: str = "PROJECT_GUTENBERG_TOP_100_YESTERDAY"
    dedupe_by_url: bool = True
    initial_status: str = "PENDING"


class ManifestBuildResp(BaseRespDto):
    status: str = ""
    files_read: int = 0
    records_found: int = 0
    records_inserted: int = 0
    records_skipped_duplicate: int = 0
    message: str = ""


# ---- Ingest pending ----
class IngestPendingReq(BaseReqDto):
    limit: int = 1000
    # Stores to ingest into. Empty -> use configured defaults.
    vector_stores: list[str] = []
    consumer_count: int = 10


class IngestPendingResp(BaseRespDto):
    status: str = ""
    queued_count: int = 0
    consumer_started: bool = False
    consumer_count: int = 0
    vector_stores: list[str] = []
    message: str = ""


# ---- Status ----
class IngestStatusResp(BaseRespDto):
    counts_by_status: dict = {}
    consumers_running: dict = {}
    queue_depth: dict = {}
