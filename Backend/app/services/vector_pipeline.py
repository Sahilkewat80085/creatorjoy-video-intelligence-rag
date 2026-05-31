import uuid
from app.models.schemas import VideoData, TranscriptChunk
from app.services.chunker import TranscriptChunker
from app.services.embedder import EmbeddingService
from app.services.qdrant_store import QdrantStore

class VectorPipeline:
    def __init__(self):
        self.chunker = TranscriptChunker()
        self.embedder = EmbeddingService()
        self.store = QdrantStore()
        
    def process_video(self, video: VideoData, label: str = None):
        # Fallback to caption if transcript is empty (common for Instagram reels)
        text_content = video.transcript or video.caption or ""
        
        print(f"Processing video {video.video_id} ({video.platform}) as {label or 'unlabeled'}...")
        
        # Build a highly descriptive metadata header prepended to the chunk text.
        # This allows the LLM to query structured metadata directly from the RAG context!
        metadata_header = "Video Metadata:\n"
        if label:
            metadata_header += f"- Label: {label}\n"
            
        metadata_header += (
            f"- Platform: {video.platform}\n"
            f"- Video ID: {video.video_id}\n"
            f"- Source URL: {video.source_url}\n"
            f"- Creator Username: {video.creator}\n"
            f"- Creator Name: {video.creator_name or 'N/A'}\n"
            f"- Views: {video.views:,}\n"
            f"- Likes: {video.likes:,}\n"
            f"- Comments: {video.comments:,}\n"
            f"- Engagement Rate: {video.engagement_rate}%\n"
        )
        if video.caption:
            metadata_header += f"- Caption: {video.caption}\n"
            
        metadata_header += "\nTranscript/Content:\n"
        
        if text_content:
            raw_chunks = self.chunker.chunk(text_content)
        else:
            raw_chunks = ["No transcript or caption available."]
        
        # Process and store the first chunk (as requested in specifications)
        for i, text in enumerate(raw_chunks[:1]):
            full_chunk_text = metadata_header + text
            
            chunk_id = str(uuid.uuid4())
            
            chunk = TranscriptChunk(
                chunk_id=chunk_id,
                video_id=video.video_id,
                platform=video.platform,
                label=label,
                chunk_index=i,
                text=full_chunk_text,
                source_url=video.source_url
            )
            
            embedding = self.embedder.embed(full_chunk_text)
            
            self.store.store_chunk(chunk, embedding)
            print(f"Stored chunk {i} for video {video.video_id}")
