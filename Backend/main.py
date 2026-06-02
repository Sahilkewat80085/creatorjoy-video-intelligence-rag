from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.ingest import router as ingest_router
from app.api.chat import router as chat_router
from dotenv import load_dotenv, find_dotenv

# Ensure environment variables are loaded for the app
load_dotenv(find_dotenv())

from contextlib import asynccontextmanager
import os
import logging
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup validation
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    print(f"[QDRANT] Checking QDRANT_URL presence: {'Yes' if qdrant_url else 'No'}")
    print(f"[QDRANT] Checking QDRANT_API_KEY presence: {'Yes' if qdrant_api_key else 'No'}")
    
    if not qdrant_url or not qdrant_api_key:
        raise ValueError("[QDRANT] Connection failed: invalid URL or API key (missing variables)")
        
    try:
        print("[QDRANT] Connecting to cloud cluster...")
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        client.get_collections()
        print("[QDRANT] Connection successful")
    except Exception as e:
        raise ConnectionError(f"[QDRANT] Connection failed: {e}")
        
    yield
    # Shutdown logic if any

app = FastAPI(title="CreatorJoy Video Intelligence API", lifespan=lifespan)

# Allow the Next.js dev server (and any local origin) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow any frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(ingest_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": "Welcome to CreatorJoy API. Visit /docs for Swagger UI."}
