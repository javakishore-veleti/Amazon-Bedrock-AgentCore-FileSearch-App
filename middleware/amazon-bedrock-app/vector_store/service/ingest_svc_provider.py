"""Provider that resolves the IngestService dependency from the factory.

The concrete implementation registers itself at startup (see bootstrap.py), so
neither this provider nor the controller imports the Impl class.
"""

from common.interfaces.ingest import IngestService
from common.objects_factory import OBJECTS_FACTORY


def get_ingest_service() -> IngestService:
    """Return the singleton ``IngestService`` registered at startup."""
    return OBJECTS_FACTORY.get(IngestService.__name__)
