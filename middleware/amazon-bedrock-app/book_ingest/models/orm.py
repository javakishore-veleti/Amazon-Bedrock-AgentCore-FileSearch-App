from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# BIGSERIAL on Postgres, but SQLite only autoincrements INTEGER PRIMARY KEY.
PrimaryKey = BigInteger().with_variant(Integer, "sqlite")


class Base(DeclarativeBase):
    pass


class VectorIngestManifest(Base):
    __tablename__ = "vector_ingest_manifest"

    id: Mapped[int] = mapped_column(PrimaryKey, primary_key=True, autoincrement=True)
    sequence_number: Mapped[int | None] = mapped_column(Integer)
    source: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    source_page_url: Mapped[str | None] = mapped_column(Text)
    txt_url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    ebook_id: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(Text)
    source_hash: Mapped[str | None] = mapped_column(Text)
    openai_file_id: Mapped[str | None] = mapped_column(Text)
    vector_store_id: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class VectorIngestSection(Base):
    __tablename__ = "vector_ingest_sections"

    id: Mapped[int] = mapped_column(PrimaryKey, primary_key=True, autoincrement=True)
    manifest_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("vector_ingest_manifest.id"))
    section_type: Mapped[str | None] = mapped_column(Text)
    section_title: Mapped[str | None] = mapped_column(Text)
    chapter_title: Mapped[str | None] = mapped_column(Text)
    start_char: Mapped[int | None] = mapped_column(Integer)
    end_char: Mapped[int | None] = mapped_column(Integer)
    chunk_file_name: Mapped[str | None] = mapped_column(Text)
    openai_file_id: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)


class VectorIngestLog(Base):
    """Append-only log of ingestion events per (book, vector store)."""

    __tablename__ = "vector_ingest_log"

    id: Mapped[int] = mapped_column(PrimaryKey, primary_key=True, autoincrement=True)
    manifest_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("vector_ingest_manifest.id"), nullable=False)
    vector_store_name: Mapped[str] = mapped_column(Text, nullable=False)
    event: Mapped[str] = mapped_column(Text, nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)


class VectorIngestTarget(Base):
    """Per (book, vector store) ingestion state -- enables ingesting one book
    into multiple stores concurrently, each tracked independently."""

    __tablename__ = "vector_ingest_targets"
    __table_args__ = (
        UniqueConstraint("manifest_id", "vector_store_name", name="uq_manifest_store"),
    )

    id: Mapped[int] = mapped_column(PrimaryKey, primary_key=True, autoincrement=True)
    manifest_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("vector_ingest_manifest.id"), nullable=False)
    vector_store_name: Mapped[str] = mapped_column(Text, nullable=False)
    vector_store_id: Mapped[str | None] = mapped_column(Text)
    provider_file_id: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class JobExecution(Base):
    """One row per API/workflow execution. ``picked_up_by_id`` self-references
    the execution that consumed this one, so executions form a lineage chain
    (dataset_build -> manifest_build -> ingest_pending)."""

    __tablename__ = "job_execution"

    id: Mapped[int] = mapped_column(PrimaryKey, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    job_type: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)
    picked_up: Mapped[bool] = mapped_column(Boolean, default=False)
    picked_up_by_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("job_execution.id")
    )
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
