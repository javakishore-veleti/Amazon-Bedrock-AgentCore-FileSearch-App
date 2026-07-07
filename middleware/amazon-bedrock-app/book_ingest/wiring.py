"""Imports every book_ingest @component module so the decorators register the
classes for wire_components(). Imported once by the app bootstrap.
"""

# config + db
import book_ingest.config.settings  # noqa: F401
import book_ingest.db.database  # noqa: F401

# dao
import book_ingest.dao.manifest_repo  # noqa: F401
import book_ingest.dao.target_repo  # noqa: F401
import book_ingest.dao.section_repo  # noqa: F401
import book_ingest.dao.log_repo  # noqa: F401
import book_ingest.dao.batch_file_dao  # noqa: F401
import book_ingest.dao.job_execution_repo  # noqa: F401
import book_ingest.dao.app_state_repo  # noqa: F401

# integrations
import book_ingest.integrations.gutenberg.client  # noqa: F401
import book_ingest.integrations.openai.client  # noqa: F401
import book_ingest.integrations.pgvector.embeddings  # noqa: F401
import book_ingest.integrations.pgvector.client  # noqa: F401

# jobs
import book_ingest.jobs.job_service  # noqa: F401

# services
import book_ingest.service.text_cleaning  # noqa: F401
import book_ingest.service.metadata  # noqa: F401
import book_ingest.service.duplicate_detection  # noqa: F401
import book_ingest.service.gutenberg_dataset_build  # noqa: F401
import book_ingest.service.manifest_build  # noqa: F401

# messaging
import book_ingest.messaging.queue.in_memory  # noqa: F401
import book_ingest.messaging.publisher.in_memory  # noqa: F401
import book_ingest.messaging.consumer.manager  # noqa: F401

# facades
import book_ingest.messaging.consumer.book_ingestion_facade  # noqa: F401
import book_ingest.facade.dataset_manifest_build_facade  # noqa: F401
import book_ingest.facade.vector_store_ingest_facade  # noqa: F401
import book_ingest.facade.pipeline_facade  # noqa: F401
