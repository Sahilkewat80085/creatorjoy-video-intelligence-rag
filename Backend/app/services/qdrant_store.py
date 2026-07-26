import os
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)
from app.models.schemas import TranscriptChunk

logger = logging.getLogger(__name__)


class QdrantStore:
    COLLECTION_NAME = "video_chunks"

    def __init__(self):
        """
        Initializes the Qdrant client using credentials loaded from environment variables.
        Silences client-server compatibility checks if necessary.
        """
        qdrant_url = os.getenv("QDRANT_URL", "").strip()
        qdrant_api_key = os.getenv("QDRANT_API_KEY", "").strip()

        if not qdrant_url or not qdrant_api_key:
            err_msg = "Connection failed: missing QDRANT_URL or QDRANT_API_KEY environment variables."
            logger.error(err_msg)
            raise ValueError(err_msg)

        try:
            # check_compatibility=False silences compatibility warnings when server endpoints don't return version info
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
                check_compatibility=False
            )
            logger.info("QdrantClient successfully initialized.")
        except Exception as e:
            logger.exception("Failed to instantiate QdrantClient.")
            raise e

    def create_collection(self):
        """
        Creates the target Qdrant collection if it does not already exist.
        """
        try:
            collections = self.client.get_collections()
            existing = [c.name for c in collections.collections]

            if self.COLLECTION_NAME not in existing:
                logger.info("Creating Qdrant collection: %s", self.COLLECTION_NAME)
                self.client.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=384,
                        distance=Distance.COSINE
                    )
                )
                logger.info("Collection '%s' successfully created.", self.COLLECTION_NAME)
            else:
                logger.info("Collection '%s' already exists.", self.COLLECTION_NAME)
        except Exception as e:
            logger.exception("Error while creating or checking Qdrant collection '%s'.", self.COLLECTION_NAME)
            raise e

    def recreate_collection(self):
        """
        Drops and recreates the target collection, clearing all existing data.
        """
        logger.info("Recreating collection '%s' (clearing old data)...", self.COLLECTION_NAME)
        try:
            self.client.delete_collection(self.COLLECTION_NAME)
        except Exception as e:
            logger.warning("Failed to delete collection '%s' (it may not exist yet): %s", self.COLLECTION_NAME, e)
            
        self.create_collection()

    def store_chunk(self, chunk: TranscriptChunk, embedding: list[float]):
        """
        Upserts a single TranscriptChunk and its embedding into Qdrant.
        
        Args:
            chunk: The TranscriptChunk metadata.
            embedding: The dense vector representation of the chunk text.
        """
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
        
        try:
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=[point]
            )
            logger.debug("Successfully upserted chunk_id: %s", chunk.chunk_id)
        except Exception as e:
            logger.exception("Failed to upsert chunk_id %s into Qdrant collection '%s'.", chunk.chunk_id, self.COLLECTION_NAME)
            raise e

    def search(self, query_embedding: list[float], limit: int = 3):
        """
        Queries Qdrant for top-K nearest neighbors based on cosine similarity.
        
        Args:
            query_embedding: The dense query vector.
            limit: The maximum number of points to return.
            
        Returns:
            A list of retrieved point structures containing payloads.
        """
        try:
            results = self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_embedding,
                limit=limit
            )
            logger.info("Search query returned %d points.", len(results.points))
            return results.points
        except Exception as e:
            logger.exception("Search query failed on Qdrant collection '%s'.", self.COLLECTION_NAME)
            raise e


