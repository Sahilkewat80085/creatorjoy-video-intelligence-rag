from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)
from app.models.schemas import TranscriptChunk


class QdrantStore:

    COLLECTION_NAME = "video_chunks"

    def __init__(self):
        import os
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if not qdrant_url or not qdrant_api_key:
            raise ValueError("[QDRANT] Connection failed: missing QDRANT_URL or QDRANT_API_KEY environment variables")

        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
        )

    def create_collection(self):

        collections = self.client.get_collections()

        existing = [
            c.name
            for c in collections.collections
        ]

        if self.COLLECTION_NAME not in existing:

            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE
                )
            )

            print("Collection created")

        else:

            print("Collection already exists")

    def recreate_collection(self):
        print("Recreating collection (clearing old data)...")
        try:
            self.client.delete_collection(self.COLLECTION_NAME)
        except Exception:
            pass
        self.create_collection()

    def store_chunk(self, chunk: TranscriptChunk, embedding: list[float]):
        point = PointStruct(
            id=chunk.chunk_id,
            vector=embedding,
            payload={
                "video_id": chunk.video_id,
                "platform": chunk.platform,
                "label": chunk.label,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "source_url": chunk.source_url
            }
        )
        
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[point]
        )

    def search(self, query_embedding: list[float], limit: int = 3):
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_embedding,
            limit=limit
        )
        # return the points list which matches the expected return format
        return results.points

