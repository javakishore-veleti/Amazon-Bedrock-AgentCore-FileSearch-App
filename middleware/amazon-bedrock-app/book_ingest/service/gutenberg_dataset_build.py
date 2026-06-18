import logging
from datetime import datetime, timezone

from book_ingest.config.settings import BookIngestSettings
from common.interfaces.book_repositories import DatasetBatchFileDao
from book_ingest.integrations.gutenberg.client import GutenbergClient
from book_ingest.models.dtos import DatasetBuildReq, DatasetBuildResp
from common.interfaces.book_services import GutenbergDatasetBuildService
from common.di import component

LOGGER = logging.getLogger(__name__)


@component(
    key="GutenbergDatasetBuildService",
    depends_on=["GutenbergClient", "DatasetBatchFileDao", "BookIngestSettings"],
)
class GutenbergDatasetBuildServiceImpl(GutenbergDatasetBuildService):
    def __init__(self, gutenberg: GutenbergClient,
                 batch_dao: DatasetBatchFileDao, settings: BookIngestSettings):
        self.gutenberg = gutenberg
        self.batch_dao = batch_dao
        self.settings = settings

    def build(self, req: DatasetBuildReq) -> DatasetBuildResp:
        LOGGER.info("dataset_build_started url=%s", req.source_url)
        discovered = self.gutenberg.fetch_top_100(req.source_url, limit=req.target_count)

        items = []
        for seq, book in enumerate(discovered, start=1):
            ebook_id = book["ebook_id"]
            items.append({
                "sequence": seq,
                "title": book.get("title"),
                "author": book.get("author"),
                "source_page_url": book.get("source_page_url"),
                "txt_url": self.gutenberg.resolve_txt_url(ebook_id),
                "ebook_id": ebook_id,
                "source": "Project Gutenberg",
                "license_family": "public_domain_or_gutenberg_license",
                "status": "DISCOVERED",
            })

        output_dir = req.output_dir or self.settings.batch_output_dir
        batch_size = req.batch_size or self.settings.batch_size
        files = self._write_batches(items, output_dir, batch_size, req.source)

        LOGGER.info("dataset_build_completed discovered=%d written=%d files=%d",
                    len(discovered), len(items), len(files))
        return DatasetBuildResp(
            request_id=req.request_id,
            status="completed",
            source_url=req.source_url,
            books_discovered=len(discovered),
            books_written=len(items),
            batch_files_created=files,
            message="Dataset batch files created successfully",
        )

    def _write_batches(self, items, output_dir, batch_size, source):
        files = []
        for start in range(0, len(items), batch_size):
            chunk = items[start:start + batch_size]
            seq = self.batch_dao.next_sequence(output_dir)
            batch_id = f"novels_batch_{seq:06d}"
            batch = {
                "batch_id": batch_id,
                "source": source,
                "source_url": self.settings.gutenberg_top_100_url,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "count": len(chunk),
                "items": chunk,
            }
            files.append(self.batch_dao.write_batch(output_dir, batch))
        return files
