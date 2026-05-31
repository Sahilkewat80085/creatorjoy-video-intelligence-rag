from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams
)


class QdrantStore:

    COLLECTION_NAME = "video_chunks"

    def __init__(self):

        self.client = QdrantClient(
            host="localhost",
            port=6333
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
