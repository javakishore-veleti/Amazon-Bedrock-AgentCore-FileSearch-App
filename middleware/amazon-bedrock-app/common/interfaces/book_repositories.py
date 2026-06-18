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


class AppStateRepository:
    """Persisted key/value app state (e.g. auto-created vector store ids)."""

    def get(self, key: str) -> str | None:
        raise NotImplementedError

    def set(self, key: str, value: str) -> None:
        raise NotImplementedError


class JobExecutionRepository:
    """Persists every API/workflow execution and the lineage between them."""

    def create(self, job_id: str, job_type: str) -> int:
        raise NotImplementedError

    def update(self, job_id: str, status: str, result: str = None,
               error: str = None) -> None:
        raise NotImplementedError

    def mark_latest_picked_up(self, consumed_job_type: str,
                              picked_up_by_id: int) -> None:
        raise NotImplementedError

    def get_by_job_id(self, job_id: str):
        raise NotImplementedError

    def latest(self, job_type: str):
        raise NotImplementedError

    def list(self, limit: int = 100) -> list:
        raise NotImplementedError
