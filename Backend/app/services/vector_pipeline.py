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
        
    def process_video(self, video: VideoData):
        if not video.transcript:
            print(f"No transcript for video {video.video_id}. Skipping.")
            return
            
        print(f"Chunking transcript for {video.video_id}...")
        raw_chunks = self.chunker.chunk(video.transcript)
        
        # Test with one chunk as requested
        for i, text in enumerate(raw_chunks[:1]):
            # Qdrant requires UUIDs (or integers) for Point IDs
            chunk_id = str(uuid.uuid4())
            
            chunk = TranscriptChunk(
                chunk_id=chunk_id,
                video_id=video.video_id,
                platform=video.platform,
                chunk_index=i,
                text=text,
                source_url=video.source_url
            )
            
            embedding = self.embedder.embed(text)
            
            self.store.store_chunk(chunk, embedding)
            print(f"Stored chunk {i}")
