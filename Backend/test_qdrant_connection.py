import os
import sys
import logging
from dotenv import load_dotenv, find_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def mask_key(key: str) -> str:
    """
    Masks sensitive API key strings to prevent credentials leakage in logger files.
    """
    if not key:
        return "None"
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


def test_qdrant_connection() -> None:
    logger.info("Starting Qdrant Cloud Connection and CRUD Validation Test...")
    load_dotenv(find_dotenv())
    
    raw_url = os.getenv("QDRANT_URL", "")
    raw_key = os.getenv("QDRANT_API_KEY", "")
    
    qdrant_url = raw_url.strip()
    qdrant_api_key = raw_key.strip()
    
    logger.info("QDRANT_URL target: %s", qdrant_url)
    logger.info("QDRANT_API_KEY masked: %s", mask_key(qdrant_api_key))
    
    if not qdrant_url or not qdrant_api_key:
        logger.error("Missing QDRANT_URL or QDRANT_API_KEY variables in environment configuration.")
        sys.exit(1)

    logger.info("Testing connection to cluster endpoint...")
    try:
        # check_compatibility=False suppresses compatibility warnings
        client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            check_compatibility=False
        )
        collections = client.get_collections()
        logger.info("[QDRANT] Endpoint connection successful.")
        logger.info("Available collections: %s", [c.name for c in collections.collections])
        
    except Exception as e:
        logger.exception("[QDRANT] Endpoint connection failed.")
        sys.exit(1)

    logger.info("Testing read/write operations on connection test collection...")
    test_collection = "connection_test"
    
    try:
        # Delete pre-existing collection to ensure clean validation setup
        try:
            client.delete_collection(test_collection)
        except Exception:
            pass
            
        logger.info("Creating test collection '%s'...", test_collection)
        client.create_collection(
            collection_name=test_collection,
            vectors_config=VectorParams(size=4, distance=Distance.COSINE)
        )
        
        logger.info("Inserting test vector point...")
        client.upsert(
            collection_name=test_collection,
            points=[
                PointStruct(
                    id=1,
                    vector=[0.1, 0.2, 0.3, 0.4],
                    payload={"test": "data"}
                )
            ]
        )
        
        logger.info("Reading test vector back from collection...")
        result = client.retrieve(
            collection_name=test_collection,
            ids=[1]
        )
        
        if result and len(result) > 0:
            logger.info("Successfully retrieved vector payload: %s", result[0].payload)
        else:
            raise ValueError("Failed to retrieve upserted vector.")
            
        logger.info("Deleting test collection '%s'...", test_collection)
        client.delete_collection(test_collection)
        
        logger.info("Qdrant read/write operations test passed successfully!")
        sys.exit(0)
        
    except Exception as e:
        logger.exception("[QDRANT] Operations test failed.")
        sys.exit(1)


if __name__ == "__main__":
    test_qdrant_connection()

