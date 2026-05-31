from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.ingestion_service import IngestionService
from app.services.vector_pipeline import VectorPipeline

router = APIRouter()

# Initialize services at module scope
ingestion_service = IngestionService()
vector_pipeline = VectorPipeline()

class IngestRequest(BaseModel):
    youtube_url: Optional[str] = None
    instagram_url: Optional[str] = None

@router.post("/api/ingest")
def ingest(request: IngestRequest):
    # Clear the old data before inserting new videos
    vector_pipeline.store.recreate_collection()
    
    result = {"status": "success"}
    
    if request.youtube_url:
        video_data = ingestion_service.youtube_provider.extract(request.youtube_url)
        vector_pipeline.process_video(video_data, label="Video A")
        result["video_a"] = video_data.model_dump()
        
    if request.instagram_url:
        video_data = ingestion_service.instagram_provider.extract(request.instagram_url)
        vector_pipeline.process_video(video_data, label="Video B")
        result["video_b"] = video_data.model_dump()
        
    return result
