"""Dependency providers: resolve facades from the ObjectsFactory for controllers."""

from common.objects_factory import OBJECTS_FACTORY


def get_dataset_manifest_build_facade():
    return OBJECTS_FACTORY.get("DatasetManifestBuildFacade")


def get_vector_store_ingest_facade():
    return OBJECTS_FACTORY.get("VectorStoreIngestFacade")


def get_ingest_status_facade():
    return OBJECTS_FACTORY.get("IngestStatusFacade")
