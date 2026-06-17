"""
Amazon Bedrock Agent Core File Search Application
Main entry point for the Python backend service
"""

import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import boto3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from common.base_classes import BaseReqDto, BaseRespDto
from ingest.api.ingest_controller import router as ingest_router
from end_points.api.end_points_controller import router as end_points_router
from bootstrap import register_services


class SearchReq(BaseReqDto):
    """Request body for a file search."""

    query: str


class SearchResp(BaseRespDto):
    """Result of a file search."""

    results: list
    query: str
    message: str

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OpenAPI tag metadata (controls grouping/order in Swagger UI)
tags_metadata = [
    {"name": "health", "description": "Service liveness checks."},
    {"name": "files", "description": "List and retrieve searchable files."},
    {"name": "search", "description": "Search files using the Bedrock agent."},
    {"name": "ingest", "description": "Ingest files into a vector store."},
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

# Register controllers / routers
app.include_router(ingest_router)
app.include_router(end_points_router)

# AWS Bedrock client
bedrock_client = None


def initialize_bedrock_client():
    """Initialize AWS Bedrock client"""
    global bedrock_client
    try:
        bedrock_client = boto3.client(
            'bedrock-agent-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
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


@app.post("/api/search", response_model=SearchResp, tags=["search"])
async def search_files(req: SearchReq) -> SearchResp:
    """Search files using Bedrock agent"""
    # TODO: Implement Bedrock agent invocation
    logger.info(f"Received search query: {req.query}")

    return SearchResp(
        results=[],
        query=req.query,
        message="Search functionality not yet implemented",
    )


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

    port = int(os.getenv('PYTHON_PORT', 8000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'

    logger.info(f"Starting server on port {port} (debug: {debug})")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug
    )
