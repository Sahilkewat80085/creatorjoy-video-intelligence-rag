import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from dotenv import load_dotenv, find_dotenv
from app.api.ingest import router as ingest_router
from app.api.chat import router as chat_router

# Setup logger configuration for entry point
logger = logging.getLogger(__name__)

# Ensure environment variables are loaded
load_dotenv(find_dotenv())


def mask_key(key: str) -> str:
    """
    Masks a sensitive API key to prevent exposing it in standard logs.
    """
    if not key:
        return "None"
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup lifespan tasks, validating connection credentials
    and checking Qdrant and Apify service availabilities.
    """
    logger.info("Starting CreatorJoy Video RAG application startup validation...")
    
    raw_url = os.getenv("QDRANT_URL", "")
    raw_key = os.getenv("QDRANT_API_KEY", "")
    apify_token = os.getenv("APIFY_API_TOKEN", "").strip()
    
    qdrant_url = raw_url.strip()
    qdrant_api_key = raw_key.strip()
    
    logger.info("QDRANT_URL target: %s", qdrant_url)
    logger.info("QDRANT_API_KEY masked: %s", mask_key(qdrant_api_key))
    logger.info("APIFY_API_TOKEN presence: %s", "Yes" if apify_token else "No")
    
    if not qdrant_url or not qdrant_api_key:
        err_msg = "[QDRANT] Connection failed: invalid URL or API key (missing environment variables)"
        logger.error(err_msg)
        raise ValueError(err_msg)
        
    try:
        logger.info("[QDRANT] Verifying connection to Qdrant cloud cluster...")
        # check_compatibility=False silences compatibility warnings
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, check_compatibility=False)
        client.get_collections()
        logger.info("[QDRANT] Cloud database connection verified successfully.")
    except Exception as e:
        err_msg = f"[QDRANT] Cloud database connection verification failed: {e}"
        logger.error(err_msg)
        raise ConnectionError(err_msg) from e
        
    yield
    logger.info("Shutting down application...")


app = FastAPI(title="CreatorJoy Video Intelligence API", lifespan=lifespan)

# Allow the Next.js dev server (and any local origin) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(ingest_router)
app.include_router(chat_router)


@app.get("/")
def root():
    """
    Root API endpoint yielding welcome message.
    """
    return {"message": "Welcome to CreatorJoy API. Visit /docs for Swagger UI."}

