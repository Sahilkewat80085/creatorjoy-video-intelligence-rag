import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.ingestion_service import IngestionService
from app.services.vector_pipeline import VectorPipeline

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services at module scope
try:
    ingestion_service = IngestionService()
    vector_pipeline = VectorPipeline()
except Exception as e:
    logger.exception("Failed to initialize IngestionService or VectorPipeline in app/api/ingest.py.")
    ingestion_service = None
    vector_pipeline = None


class IngestRequest(BaseModel):
    video_a_url: Optional[str] = None
    video_b_url: Optional[str] = None


def get_video_provider(url: str, service: IngestionService) -> Any:
    """
    Identifies and returns the video provider based on the platform URL.
    
    Args:
        url: The media page URL.
        service: IngestionService instance.
        
    Returns:
        The provider object.
        
    Raises:
        HTTPException: If the platform is unsupported.
    """
    if not url or not isinstance(url, str):
        raise HTTPException(status_code=400, detail="Invalid media URL provided.")
        
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return service.youtube_provider
    elif "instagram.com" in url_lower:
        return service.instagram_provider
    else:
        logger.warning("Unsupported URL platform requested: %s", url)
        raise HTTPException(status_code=400, detail=f"Unsupported URL platform: {url}")


@router.post("/api/ingest")
def ingest(request: IngestRequest) -> Dict[str, Any]:
    """
    API endpoint to ingest media data from video URLs.
    Drops the current vector store collection and creates a fresh indexes.
    
    Args:
        request: IngestRequest body containing URLs.
        
    Returns:
        Ingestion status response.
    """
    logger.info("Received ingestion request. URLs: video_a_url=%s, video_b_url=%s", request.video_a_url, request.video_b_url)
    
    if ingestion_service is None or vector_pipeline is None:
        logger.error("IngestionService or VectorPipeline not initialized.")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Backend services are not initialized."}
        )

    # Recreate/clear vector store collection before loading new data
    try:
        logger.info("Recreating vector store collection '%s' to clear old data...", vector_pipeline.store.COLLECTION_NAME)
        vector_pipeline.store.recreate_collection()
    except Exception as e:
        logger.exception("Vector database was unreachable during collection recreation.")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "Vector database unavailable",
                "detail": str(e)
            }
        )
    
    result: Dict[str, Any] = {"status": "success"}
    
    # Ingest Video A
    if request.video_a_url:
        try:
            logger.info("Processing Video A URL: %s", request.video_a_url)
            provider = get_video_provider(request.video_a_url, ingestion_service)
            video_data = provider.extract(request.video_a_url)
            if not video_data:
                raise ValueError("Provider extracted empty video data.")
                
            video_data = ingestion_service._apply_whisper_fallback(video_data)
            vector_pipeline.process_video(video_data, label="Video A")
            result["video_a"] = video_data.model_dump()
            logger.info("Video A successfully processed and ingested.")
        except Exception as e:
            logger.exception("Failed to ingest Video A from URL: %s", request.video_a_url)
            raise HTTPException(status_code=422, detail=f"Failed to ingest Video A: {str(e)}")
        
    # Ingest Video B
    if request.video_b_url:
        try:
            logger.info("Processing Video B URL: %s", request.video_b_url)
            provider = get_video_provider(request.video_b_url, ingestion_service)
            video_data = provider.extract(request.video_b_url)
            if not video_data:
                raise ValueError("Provider extracted empty video data.")
                
            video_data = ingestion_service._apply_whisper_fallback(video_data)
            vector_pipeline.process_video(video_data, label="Video B")
            result["video_b"] = video_data.model_dump()
            logger.info("Video B successfully processed and ingested.")
        except Exception as e:
            logger.exception("Failed to ingest Video B from URL: %s", request.video_b_url)
            raise HTTPException(status_code=422, detail=f"Failed to ingest Video B: {str(e)}")
        
    return result

