from typing import Optional, List

from pydantic import BaseModel


class VideoData(BaseModel):
    platform: str
    video_id: str
    source_url: str

    creator: str
    creator_name: Optional[str] = None

    views: int = 0
    likes: int = 0
    comments: int = 0

    engagement_rate: float = 0.0

    hashtags: List[str] = []

    caption: Optional[str] = None
    transcript: Optional[str] = None

    duration: Optional[int] = None


class TranscriptChunk(BaseModel):
    chunk_id: str

    video_id: str
    platform: str
    label: Optional[str] = None

    chunk_index: int

    text: str

    source_url: str