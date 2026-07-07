"""
Amazon Bedrock Agent Core File Search Application
Main entry point for the Python backend service
"""

import logging
from contextlib import asynccontextmanager

import boto3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from end_points.api.end_points_controller import router as end_points_router
from book_ingest.api.dataset_controller import router as book_dataset_router
from book_ingest.api.manifest_controller import router as book_manifest_router
from book_ingest.api.ingest_controller import router as book_ingest_router
from book_ingest.api.jobs_controller import router as book_jobs_router
from search.api.search_controller import router as search_router
from bootstrap import register_services
from common.observability import configure_observability
from common.observability.http_middleware import RequestContextMiddleware
from config.app_settings import get_app_settings, load_app_settings

# Startup order: profile → observability → (later) register_services in lifespan
_app_settings = load_app_settings()
configure_observability(_app_settings)
logger = logging.getLogger(__name__)

# OpenAPI tag metadata (controls grouping/order in Swagger UI)
tags_metadata = [
    {"name": "health", "description": "Service liveness checks."},
    {"name": "files", "description": "List and retrieve searchable files."},
    {"name": "search", "description": "Search ingested books in the vector store."},
    {"name": "book-dataset", "description": "Build Gutenberg dataset batch files."},
    {"name": "book-manifest", "description": "Build the ingestion manifest from batch files."},
    {"name": "book-ingest", "description": "Queue pending books and run concurrent ingestion."},
    {"name": "jobs", "description": "Poll status of async jobs (dataset/manifest/ingest)."},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hooks. Registers service implementations at startup."""
    register_services()
    yield


# Initialize FastAPI app
app = FastAPI(
    title="Amazon Bedrock Agent Core File Search",
    description="API for intelligent file search using Bedrock agents",
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)

# Register controllers / routers
app.include_router(end_points_router)
app.include_router(book_dataset_router)
app.include_router(book_manifest_router)
app.include_router(book_ingest_router)
app.include_router(book_jobs_router)
app.include_router(search_router)

# AWS Bedrock client
bedrock_client = None


def initialize_bedrock_client():
    """Initialize AWS Bedrock client"""
    global bedrock_client
    try:
        aws = get_app_settings().aws
        client_kwargs: dict = {"region_name": aws.region}
        if aws.access_key_id and aws.secret_access_key:
            client_kwargs["aws_access_key_id"] = aws.access_key_id
            client_kwargs["aws_secret_access_key"] = aws.secret_access_key
        bedrock_client = boto3.client("bedrock-agent-runtime", **client_kwargs)
        logger.info("Bedrock client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock client: {e}")
        raise


@app.get("/", include_in_schema=False)
async def root():
    """Redirect the root path to the Swagger UI."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "bedrock-filesearch",
        "version": "1.0.0"
    }


@app.get("/api/files", tags=["files"])
async def list_files():
    """List available files for searching"""
    try:
        # TODO: Implement file listing logic
        return {
            "files": [],
            "message": "File listing not yet implemented"
        }
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return {"error": str(e)}, 500


@app.get("/api/files/{file_id}", tags=["files"])
async def get_file(file_id: str):
    """Retrieve specific file details"""
    try:
        # TODO: Implement file retrieval logic
        return {
            "file_id": file_id,
            "message": "File retrieval not yet implemented"
        }
    except Exception as e:
        logger.error(f"Error retrieving file: {e}")
        return {"error": str(e)}, 500


if __name__ == "__main__":
    import uvicorn

    app_cfg = get_app_settings().app
    port = app_cfg.python_port
    debug = app_cfg.debug

    logger.info("Starting server on port %s (debug: %s, profile: %s)",
                port, debug, get_app_settings().profile)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug
    )
