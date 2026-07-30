from typing import Optional, List
from pydantic import BaseModel, Field


class VideoData(BaseModel):
    """
    Data model representing a video scraped from YouTube or Instagram,
    containing performance metadata, transcription contents, and media links.
    """
    platform: str = Field(
        ..., 
        description="The host social media platform of the video (e.g., 'youtube' or 'instagram')."
    )
    video_id: str = Field(
        ..., 
        description="The unique identifier extracted from the video's URL."
    )
    source_url: str = Field(
        ..., 
        description="The full original source URL of the video."
    )

    creator: str = Field(
        ..., 
        description="The username or handle of the video creator/channel owner."
    )
    creator_name: Optional[str] = Field(
        None, 
        description="The display/full name of the video creator, if available."
    )

    views: int = Field(
        0, 
        description="Total view count of the video."
    )
    likes: int = Field(
        0, 
        description="Total like count of the video."
    )
    comments: int = Field(
        0, 
        description="Total comment count of the video."
    )

    engagement_rate: float = Field(
        0.0, 
        description="Calculated engagement rate: ((likes + comments) / views) * 100."
    )

    hashtags: List[str] = Field(
        default_factory=list, 
        description="List of hashtags associated with the video description or caption."
    )

    caption: Optional[str] = Field(
        None, 
        description="The caption or description text of the post."
    )
    transcript: Optional[str] = Field(
        None, 
        description="The full transcription text of the video's audio."
    )
    transcript_source: Optional[str] = Field(
        None, 
        description="The origin of the transcript (e.g., 'native' or 'whisper')."
    )
    direct_media_url: Optional[str] = Field(
        None, 
        description="Direct download link to the audio/video media file."
    )

    duration: Optional[int] = Field(
        None, 
        description="Duration of the video in seconds."
    )


class TranscriptChunk(BaseModel):
    """
    Data model representing a single partitioned chunk of a video's transcript,
    preconfigured for embedding and indexing in the vector database.
    """
    chunk_id: str = Field(
        ..., 
        description="A unique UUID string identifying the chunk."
    )

    video_id: str = Field(
        ..., 
        description="The video_id of the parent video."
    )
    platform: str = Field(
        ..., 
        description="The source platform of the video (e.g. 'youtube')."
    )
    label: Optional[str] = Field(
        None, 
        description="A descriptive classification tag (e.g., 'Video A' or 'Video B')."
    )

    chunk_index: int = Field(
        ..., 
        description="The sequential offset index of the chunk within the transcript."
    )

    text: str = Field(
        ..., 
        description="The text content segment of this specific chunk."
    )

    source_url: str = Field(
        ..., 
        description="The parent video source URL for easy referencing in citations."
    )