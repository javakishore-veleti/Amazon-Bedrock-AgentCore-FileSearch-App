-- Runs once on first container start when the data volume is empty.
-- Embedding tables are created at runtime by PgVectorClient.ensure_store().

CREATE EXTENSION IF NOT EXISTS vector;

SELECT 'filesearch database initialized with pgvector' AS status;
