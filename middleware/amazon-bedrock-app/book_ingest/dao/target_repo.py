import logging
from datetime import datetime, timezone

from sqlalchemy import select

from book_ingest.dao.interfaces import VectorIngestTargetRepository
from book_ingest.db.database import BookIngestDatabase
from book_ingest.models.orm import VectorIngestManifest, VectorIngestTarget
from book_ingest.models.statuses import ManifestStatus
from common.di import component

LOGGER = logging.getLogger(__name__)


def _now():
    return datetime.now(timezone.utc)


@component(key="VectorIngestTargetRepository", depends_on=["BookIngestDatabase"])
class VectorIngestTargetRepositoryImpl(VectorIngestTargetRepository):
    def __init__(self, database: BookIngestDatabase):
        self.database = database

    def upsert_queued(self, manifest_id, vector_store_name, vector_store_id) -> int:
        with self.database.session() as s:
            row = s.scalar(
                select(VectorIngestTarget).where(
                    VectorIngestTarget.manifest_id == manifest_id,
                    VectorIngestTarget.vector_store_name == vector_store_name,
                )
            )
            if row is None:
                row = VectorIngestTarget(
                    manifest_id=manifest_id,
                    vector_store_name=vector_store_name,
                    vector_store_id=vector_store_id,
                    status=ManifestStatus.QUEUED.value,
                    created_at=_now(),
                    updated_at=_now(),
                )
                s.add(row)
            else:
                row.status = ManifestStatus.QUEUED.value
                row.vector_store_id = vector_store_id
                row.updated_at = _now()
            s.commit()
            return row.id

    def mark_in_progress(self, target_id):
        self._set(target_id, status=ManifestStatus.IN_PROGRESS.value)

    def mark_indexed(self, target_id, provider_file_id):
        self._set(target_id, status=ManifestStatus.INDEXED.value,
                  provider_file_id=provider_file_id, indexed=True)

    def mark_failed_retryable(self, target_id, error_message):
        self._set(target_id, status=ManifestStatus.FAILED_RETRYABLE.value,
                  error_message=error_message, bump_retry=True)

    def mark_failed_permanent(self, target_id, error_message):
        self._set(target_id, status=ManifestStatus.FAILED_PERMANENT.value,
                  error_message=error_message)

    def mark_skipped_duplicate(self, target_id):
        self._set(target_id, status=ManifestStatus.SKIPPED_DUPLICATE.value)

    def find_indexed_by_hash_for_store(self, source_hash, vector_store_name) -> bool:
        with self.database.session() as s:
            hit = s.scalar(
                select(VectorIngestTarget.id)
                .join(VectorIngestManifest,
                      VectorIngestManifest.id == VectorIngestTarget.manifest_id)
                .where(VectorIngestManifest.source_hash == source_hash,
                       VectorIngestTarget.vector_store_name == vector_store_name,
                       VectorIngestTarget.status == ManifestStatus.INDEXED.value)
            )
            return hit is not None

    def _set(self, target_id, status, provider_file_id=None, error_message=None,
             bump_retry=False, indexed=False):
        with self.database.session() as s:
            row = s.get(VectorIngestTarget, target_id)
            if not row:
                return
            row.status = status
            if provider_file_id is not None:
                row.provider_file_id = provider_file_id
            if error_message is not None:
                row.error_message = error_message
            if bump_retry:
                row.retry_count = (row.retry_count or 0) + 1
            if indexed:
                row.indexed_at = _now()
            row.updated_at = _now()
            s.commit()

    def retry_count(self, target_id) -> int:
        with self.database.session() as s:
            row = s.get(VectorIngestTarget, target_id)
            return (row.retry_count or 0) if row else 0

    def get_status(self, target_id) -> str | None:
        with self.database.session() as s:
            row = s.get(VectorIngestTarget, target_id)
            return row.status if row else None
