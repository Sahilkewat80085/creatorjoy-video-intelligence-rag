from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.ingestion_service import IngestionService
from app.services.vector_pipeline import VectorPipeline

router = APIRouter()

# Initialize services at module scope
ingestion_service = IngestionService()
vector_pipeline = VectorPipeline()

from fastapi import HTTPException

class IngestRequest(BaseModel):
    video_a_url: Optional[str] = None
    video_b_url: Optional[str] = None

def get_video_provider(url: str, ingestion_service: IngestionService):
    if "youtube.com" in url or "youtu.be" in url:
        return ingestion_service.youtube_provider
    elif "instagram.com" in url:
        return ingestion_service.instagram_provider
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported URL platform: {url}")

@router.post("/api/ingest")
def ingest(request: IngestRequest):
    # Clear the old data before inserting new videos
    from fastapi.responses import JSONResponse
    try:
        vector_pipeline.store.recreate_collection()
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "Vector database unavailable",
                "detail": str(e)
            }
        )
    
    result = {"status": "success"}
    
    if request.video_a_url:
        provider = get_video_provider(request.video_a_url, ingestion_service)
        video_data = provider.extract(request.video_a_url)
        video_data = ingestion_service._apply_whisper_fallback(video_data)
        vector_pipeline.process_video(video_data, label="Video A")
        result["video_a"] = video_data.model_dump()
        
    if request.video_b_url:
        provider = get_video_provider(request.video_b_url, ingestion_service)
        video_data = provider.extract(request.video_b_url)
        video_data = ingestion_service._apply_whisper_fallback(video_data)
        vector_pipeline.process_video(video_data, label="Video B")
        result["video_b"] = video_data.model_dump()
        
    return result
