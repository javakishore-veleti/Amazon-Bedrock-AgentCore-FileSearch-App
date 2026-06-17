from common.di import component
from configs.end_points_master import OPENAPI_VECTOR_STORE


@component(key=OPENAPI_VECTOR_STORE)
class OpenAIVectorStoreIngestFacade:
    def __init__(self, vector_store_client=None):
        self.vector_store_client = vector_store_client

    def ingest(self, documents):
        # Transform documents into the format expected by OpenAI's vector store
        transformed_docs = self._transform_documents(documents)
        # Ingest transformed documents into the vector store
        self.vector_store_client.ingest(transformed_docs)

    def _transform_documents(self, documents):
        # Placeholder for document transformation logic
        # This could include tokenization, embedding generation, etc.
        return documents
