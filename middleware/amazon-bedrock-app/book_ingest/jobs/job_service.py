"""Async job runner: submit long-running work to a background thread pool and
poll it by job id, so HTTP calls return immediately instead of timing out at
scale (e.g. building/queueing 100k books).
"""

import logging
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

from common.di import component

LOGGER = logging.getLogger(__name__)


@component(key="AsyncJobService")
class AsyncJobService:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="job")
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()

    def submit(self, job_type: str, fn) -> str:
        """Run ``fn()`` in the background; return a job id to poll."""
        job_id = str(uuid.uuid4())
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id, "job_type": job_type,
                "status": "running", "result": None, "error": None,
            }
        self._executor.submit(self._run, job_id, fn)
        LOGGER.info("job_submitted id=%s type=%s", job_id, job_type)
        return job_id

    def _run(self, job_id: str, fn):
        try:
            result = fn()
            data = result.model_dump() if hasattr(result, "model_dump") else result
            self._set(job_id, status="completed", result=data)
            LOGGER.info("job_completed id=%s", job_id)
        except Exception as exc:  # noqa: BLE001 - record failure, don't crash pool
            LOGGER.exception("job_failed id=%s", job_id)
            self._set(job_id, status="failed", error=str(exc))

    def _set(self, job_id: str, **fields):
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(fields)

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None
