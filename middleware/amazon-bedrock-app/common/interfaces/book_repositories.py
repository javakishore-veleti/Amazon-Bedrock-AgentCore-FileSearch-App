"""Book-ingest DAO/repository interfaces (swappable per database config)."""


class VectorIngestManifestRepository:
    def insert_discovered_books(self, books: list, initial_status: str,
                               dedupe_by_url: bool) -> dict:
        raise NotImplementedError

    def find_pending_books(self, limit: int) -> list:
        raise NotImplementedError

    def mark_queued(self, manifest_id: int) -> None:
        raise NotImplementedError

    def mark_indexed_if_all_targets_done(self, manifest_id: int) -> None:
        raise NotImplementedError

    def find_indexed_by_hash(self, source_hash: str):
        raise NotImplementedError

    def set_source_hash(self, manifest_id: int, source_hash: str) -> None:
        raise NotImplementedError

    def count_by_status(self) -> dict:
        raise NotImplementedError

    def get(self, manifest_id: int):
        raise NotImplementedError


class VectorIngestTargetRepository:
    """Per (book, vector store) state -- supports multi-store ingestion."""

    def upsert_queued(self, manifest_id: int, vector_store_name: str,
                      vector_store_id: str) -> int:
        raise NotImplementedError

    def mark_in_progress(self, target_id: int) -> None:
        raise NotImplementedError

    def mark_indexed(self, target_id: int, provider_file_id: str) -> None:
        raise NotImplementedError

    def mark_failed_retryable(self, target_id: int, error_message: str) -> None:
        raise NotImplementedError

    def mark_failed_permanent(self, target_id: int, error_message: str) -> None:
        raise NotImplementedError

    def mark_skipped_duplicate(self, target_id: int) -> None:
        raise NotImplementedError

    def find_indexed_by_hash_for_store(self, source_hash: str,
                                       vector_store_name: str) -> bool:
        raise NotImplementedError


class VectorIngestLogRepository:
    def append(self, manifest_id: int, vector_store_name: str, event: str,
               message: str = "") -> None:
        raise NotImplementedError


class VectorIngestSectionRepository:
    def save_sections(self, manifest_id: int, sections: list) -> None:
        raise NotImplementedError

    def update_section_file_id(self, section_id: int, openai_file_id: str) -> None:
        raise NotImplementedError


class DatasetBatchFileDao:
    def write_batch(self, output_dir: str, batch: dict) -> str:
        raise NotImplementedError

    def next_sequence(self, output_dir: str) -> int:
        raise NotImplementedError

    def read_batches(self, input_dir: str) -> list:
        raise NotImplementedError
