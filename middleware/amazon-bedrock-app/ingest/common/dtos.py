class IngestReq:
    def __init__(self, file_path, file_type):
        self.file_path = file_path
        self.file_type = file_type
        self.target_vector_store = "openai"  # Default vector store, can be extended to support multiple stores

class         