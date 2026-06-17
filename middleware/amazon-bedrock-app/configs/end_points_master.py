"""Master catalog of vector-store end points (INTERNAL -- not exposed via the API).

Each entry maps a human-readable end point name to an ``object_id``. The object
id is the key under which that end point's implementation is registered in the
ObjectsFactory via its ``@component(key=...)`` annotation, so the live singleton
can be resolved with ``OBJECTS_FACTORY.get(object_id)``.

The object-id constants below are the single source of truth: a vector-store
impl should annotate itself with the matching constant, e.g.
``@component(key=OPENAPI_VECTOR_STORE)``.
"""

# Cache type / end point category for all vector stores.
VECTOR_STORE_TYPE = "vector_store"

# Object ids == @component keys for each (planned) vector-store impl.
OPENAPI_VECTOR_STORE = "OpenApiVectorStoreImpl"
AWS_OPENSEARCH = "AwsOpenSearchVectorStoreImpl"
MONGODB_VECTOR = "MongoDbVectorStoreImpl"
CHROMA = "ChromaVectorStoreImpl"
PINECONE = "PineconeVectorStoreImpl"
PGVECTOR = "PgVectorVectorStoreImpl"


class EndPointMasterEntry:
    def __init__(self, name: str, object_id: str):
        self.name = name
        self.object_id = object_id

    def __repr__(self):
        return f"EndPointMasterEntry(name={self.name!r}, object_id={self.object_id!r})"


# All planned vector-store end points. Only OpenAPI is implemented so far; the
# rest are placeholders whose impls will register under the same object ids.
END_POINTS_MASTER: list[EndPointMasterEntry] = [
    EndPointMasterEntry(name="OpenAPI Vector Store", object_id=OPENAPI_VECTOR_STORE),
    EndPointMasterEntry(name="AWS OpenSearch", object_id=AWS_OPENSEARCH),
    EndPointMasterEntry(name="MongoDB Vector", object_id=MONGODB_VECTOR),
    EndPointMasterEntry(name="Chroma", object_id=CHROMA),
    EndPointMasterEntry(name="Pinecone", object_id=PINECONE),
    EndPointMasterEntry(name="PgVector", object_id=PGVECTOR),
]

# name -> object_id index for quick lookups.
END_POINTS_BY_NAME: dict[str, str] = {e.name: e.object_id for e in END_POINTS_MASTER}


def get_object_id(name: str) -> str:
    """Return the registered object id (factory key) for an end point name."""
    if name not in END_POINTS_BY_NAME:
        raise KeyError(f"Unknown end point name '{name}'")
    return END_POINTS_BY_NAME[name]
