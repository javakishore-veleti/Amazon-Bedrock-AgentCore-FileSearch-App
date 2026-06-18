import logging
from datetime import datetime, timezone

from sqlalchemy import func, select

from book_ingest.dao.interfaces import VectorIngestManifestRepository
from book_ingest.db.database import BookIngestDatabase
from book_ingest.models.orm import VectorIngestManifest, VectorIngestTarget
from book_ingest.models.statuses import ManifestStatus
from common.di import component

LOGGER = logging.getLogger(__name__)


def _now():
    return datetime.now(timezone.utc)


@component(key="VectorIngestManifestRepository", depends_on=["BookIngestDatabase"])
class VectorIngestManifestRepositoryImpl(VectorIngestManifestRepository):
    def __init__(self, database: BookIngestDatabase):
        self.database = database

    def insert_discovered_books(self, books, initial_status, dedupe_by_url) -> dict:
        inserted = skipped = 0
        with self.database.session() as s:
            for book in books:
                txt_url = book.get("txt_url")
                if not txt_url:
                    continue
                if dedupe_by_url:
                    exists = s.scalar(
                        select(VectorIngestManifest.id).where(
                            VectorIngestManifest.txt_url == txt_url
                        )
                    )
                    if exists:
                        skipped += 1
                        continue
                s.add(VectorIngestManifest(
                    sequence_number=book.get("sequence"),
                    source=book.get("source"),
                    source_url=book.get("source_url"),
                    source_page_url=book.get("source_page_url"),
                    txt_url=txt_url,
                    ebook_id=book.get("ebook_id"),
                    title=book.get("title"),
                    author=book.get("author"),
                    status=initial_status,
                    created_at=_now(),
                    updated_at=_now(),
                ))
                try:
                    s.commit()
                    inserted += 1
                except Exception as exc:  # unique txt_url race
                    s.rollback()
                    LOGGER.warning("Skipping duplicate txt_url %s: %s", txt_url, exc)
                    skipped += 1
        return {"inserted": inserted, "skipped": skipped}

    def find_pending_books(self, limit) -> list:
        statuses = [ManifestStatus.PENDING.value, ManifestStatus.FAILED_RETRYABLE.value]
        with self.database.session() as s:
            rows = s.scalars(
                select(VectorIngestManifest)
                .where(VectorIngestManifest.status.in_(statuses))
                .order_by(VectorIngestManifest.sequence_number)
                .limit(limit)
            ).all()
            return [self._to_dict(r) for r in rows]

    def mark_queued(self, manifest_id) -> None:
        self._set_status(manifest_id, ManifestStatus.QUEUED.value)

    def mark_indexed_if_all_targets_done(self, manifest_id) -> None:
        with self.database.session() as s:
            total = s.scalar(select(func.count()).select_from(VectorIngestTarget)
                             .where(VectorIngestTarget.manifest_id == manifest_id))
            indexed = s.scalar(select(func.count()).select_from(VectorIngestTarget)
                               .where(VectorIngestTarget.manifest_id == manifest_id,
                                      VectorIngestTarget.status == ManifestStatus.INDEXED.value))
            row = s.get(VectorIngestManifest, manifest_id)
            if row and total and indexed == total:
                row.status = ManifestStatus.INDEXED.value
                row.indexed_at = _now()
                row.updated_at = _now()
                s.commit()

    def find_indexed_by_hash(self, source_hash):
        with self.database.session() as s:
            return s.scalar(
                select(VectorIngestManifest).where(
                    VectorIngestManifest.source_hash == source_hash,
                    VectorIngestManifest.status == ManifestStatus.INDEXED.value,
                )
            )

    def set_source_hash(self, manifest_id, source_hash) -> None:
        with self.database.session() as s:
            row = s.get(VectorIngestManifest, manifest_id)
            if row:
                row.source_hash = source_hash
                row.updated_at = _now()
                s.commit()

    def count_by_status(self) -> dict:
        with self.database.session() as s:
            rows = s.execute(
                select(VectorIngestManifest.status, func.count())
                .group_by(VectorIngestManifest.status)
            ).all()
            return {status: count for status, count in rows}

    def get(self, manifest_id):
        with self.database.session() as s:
            row = s.get(VectorIngestManifest, manifest_id)
            return self._to_dict(row) if row else None

    def _set_status(self, manifest_id, status):
        with self.database.session() as s:
            row = s.get(VectorIngestManifest, manifest_id)
            if row:
                row.status = status
                row.updated_at = _now()
                s.commit()

    @staticmethod
    def _to_dict(row):
        return {
            "id": row.id,
            "sequence_number": row.sequence_number,
            "source": row.source,
            "source_url": row.source_url,
            "source_page_url": row.source_page_url,
            "txt_url": row.txt_url,
            "ebook_id": row.ebook_id,
            "title": row.title,
            "author": row.author,
            "status": row.status,
            "source_hash": row.source_hash,
        }
