"""Async job runner: submit long-running work to a background thread pool and
poll it by job id, so HTTP calls return immediately instead of timing out at
scale (e.g. building/queueing 100k books).

Every execution is also persisted to the job_execution table. When a job
``consumes`` a prior job type, the latest such execution is marked picked-up and
linked to this execution (picked_up_by_id), building a lineage chain.
"""

import json
import logging
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

from book_ingest.db.database import BookIngestDatabase  # noqa: F401 (doc)
from common.di import component
from common.interfaces.book_repositories import JobExecutionRepository

LOGGER = logging.getLogger(__name__)


@component(key="AsyncJobService", depends_on=["JobExecutionRepository"])
class AsyncJobService:
    def __init__(self, exec_repo: JobExecutionRepository):
        self.exec_repo = exec_repo
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="job")
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()

    def submit(self, job_type: str, fn, consumes: str = None) -> str:
        """Run ``fn()`` in the background; return a job id to poll.

        ``consumes`` names the upstream job type this run picks up (for lineage).
        """
        job_id = str(uuid.uuid4())
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id, "job_type": job_type,
                "status": "running", "result": None, "error": None,
            }
        exec_id = self.exec_repo.create(job_id, job_type)
        if consumes:
            self.exec_repo.mark_latest_picked_up(consumes, exec_id)
        self._executor.submit(self._run, job_id, fn)
        LOGGER.info("job_submitted id=%s type=%s consumes=%s", job_id, job_type, consumes)
        return job_id

    def _run(self, job_id: str, fn):
        try:
            result = fn()
            data = result.model_dump() if hasattr(result, "model_dump") else result
            self._set(job_id, status="completed", result=data)
            self.exec_repo.update(job_id, "completed",
                                  result=json.dumps(data, default=str))
            LOGGER.info("job_completed id=%s", job_id)
        except Exception as exc:  # noqa: BLE001 - record failure, don't crash pool
            LOGGER.exception("job_failed id=%s", job_id)
            self._set(job_id, status="failed", error=str(exc))
            self.exec_repo.update(job_id, "failed", error=str(exc))

    def _set(self, job_id: str, **fields):
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(fields)

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                return dict(job)
        return self.exec_repo.get_by_job_id(job_id)

    def list(self, limit: int = 100) -> list[dict]:
        return self.exec_repo.list(limit)
