import logging
from datetime import datetime, timezone

from sqlalchemy import select

from book_ingest.db.database import BookIngestDatabase
from book_ingest.models.orm import JobExecution
from common.di import component
from common.interfaces.book_repositories import JobExecutionRepository

LOGGER = logging.getLogger(__name__)


def _now():
    return datetime.now(timezone.utc)


@component(key="JobExecutionRepository", depends_on=["BookIngestDatabase"])
class JobExecutionRepositoryImpl(JobExecutionRepository):
    def __init__(self, database: BookIngestDatabase):
        self.database = database

    def create(self, job_id: str, job_type: str) -> int:
        with self.database.session() as s:
            row = JobExecution(job_id=job_id, job_type=job_type, status="running",
                               picked_up=False, created_at=_now(), updated_at=_now())
            s.add(row)
            s.commit()
            return row.id

    def update(self, job_id: str, status: str, result=None, error=None) -> None:
        with self.database.session() as s:
            row = s.scalar(select(JobExecution).where(JobExecution.job_id == job_id))
            if row:
                row.status = status
                if result is not None:
                    row.result = result
                if error is not None:
                    row.error = error
                row.updated_at = _now()
                s.commit()

    def mark_latest_picked_up(self, consumed_job_type, picked_up_by_id) -> None:
        """Mark the most recent un-consumed execution of consumed_job_type as
        picked up by the given execution id (builds the lineage chain)."""
        with self.database.session() as s:
            row = s.scalar(
                select(JobExecution)
                .where(JobExecution.job_type == consumed_job_type,
                       JobExecution.picked_up.is_(False))
                .order_by(JobExecution.id.desc())
                .limit(1)
            )
            if row:
                row.picked_up = True
                row.picked_up_by_id = picked_up_by_id
                row.updated_at = _now()
                s.commit()

    def get_by_job_id(self, job_id: str):
        with self.database.session() as s:
            row = s.scalar(select(JobExecution).where(JobExecution.job_id == job_id))
            return self._to_dict(row) if row else None

    def latest(self, job_type: str):
        with self.database.session() as s:
            row = s.scalar(
                select(JobExecution).where(JobExecution.job_type == job_type)
                .order_by(JobExecution.id.desc()).limit(1)
            )
            return self._to_dict(row) if row else None

    def list(self, limit: int = 100) -> list:
        with self.database.session() as s:
            rows = s.scalars(
                select(JobExecution).order_by(JobExecution.id.desc()).limit(limit)
            ).all()
            return [self._to_dict(r) for r in rows]

    @staticmethod
    def _to_dict(row):
        return {
            "id": row.id,
            "job_id": row.job_id,
            "job_type": row.job_type,
            "status": row.status,
            "result": row.result,
            "error": row.error,
            "picked_up": bool(row.picked_up),
            "picked_up_by_id": row.picked_up_by_id,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }
