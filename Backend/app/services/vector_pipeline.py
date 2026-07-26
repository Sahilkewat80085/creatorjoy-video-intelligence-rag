import uuid
import logging
from app.models.schemas import VideoData, TranscriptChunk
from app.services.chunker import TranscriptChunker
from app.services.embedder import EmbeddingService
from app.services.qdrant_store import QdrantStore

logger = logging.getLogger(__name__)


class VectorPipeline:
    def __init__(self):
        """
        Initializes the chunker, embedder, and vector store dependencies.
        """
        try:
            self.chunker = TranscriptChunker()
            self.embedder = EmbeddingService()
            self.store = QdrantStore()
        except Exception as e:
            logger.exception("Failed to initialize dependencies in VectorPipeline.")
            raise e
        
    def process_video(self, video: VideoData, label: str = None):
        """
        Processes a single video's metadata and transcript/caption content,
        splits it into semantic chunks, generates embeddings, and indexes them into Qdrant.
        
        Args:
            video: The VideoData model instance.
            label: Optional label (e.g., 'Video A', 'Video B') for structured querying.
        """
        # Fallback to caption if transcript is empty (common for Instagram reels)
        text_content = video.transcript or video.caption or ""
        
        logger.info("Processing video %s (%s) with label '%s'...", video.video_id, video.platform, label or 'unlabeled')
        
        # Ensure values are safe to format and not None
        views_val = video.views if video.views is not None else 0
        likes_val = video.likes if video.likes is not None else 0
        comments_val = video.comments if video.comments is not None else 0
        engagement_val = video.engagement_rate if video.engagement_rate is not None else 0.0

        views_str = f"{views_val:,}" if isinstance(views_val, (int, float)) else str(views_val)
        likes_str = f"{likes_val:,}" if isinstance(likes_val, (int, float)) else str(likes_val)
        comments_str = f"{comments_val:,}" if isinstance(comments_val, (int, float)) else str(comments_val)
        engagement_str = f"{engagement_val}%" if isinstance(engagement_val, (int, float)) else f"{engagement_val}%"

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
            f"- Views: {views_str}\n"
            f"- Likes: {likes_str}\n"
            f"- Comments: {comments_str}\n"
            f"- Engagement Rate: {engagement_str}\n"
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
            
            try:
                embedding = self.embedder.embed(full_chunk_text)
                self.store.store_chunk(chunk, embedding)
                logger.info("Successfully stored chunk %d for video %s in Qdrant.", i, video.video_id)
            except Exception as e:
                logger.exception("Failed to embed or store chunk %d for video %s.", i, video.video_id)
                raise e

