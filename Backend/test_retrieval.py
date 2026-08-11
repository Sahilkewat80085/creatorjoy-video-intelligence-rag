import sys
import os
import logging
from dotenv import load_dotenv

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

from app.services.embedder import EmbeddingService
from app.services.qdrant_store import QdrantStore

query = "What is this song about? Is it about love and relationship and feeling?"
logger.info("Retrieval Query target: '%s'", query)

try:
    logger.info("Initializing Embedder and Qdrant store services...")
    embedder = EmbeddingService()
    store = QdrantStore()

    logger.info("Generating embedding for search query...")
    query_embedding = embedder.embed(query)

    logger.info("Searching Qdrant collections...")
    results = store.search(query_embedding, limit=3)

    logger.info("Retrieval query complete. Top matching results:")
    for i, result in enumerate(results):
        print(f"\nResult {i+1} (Score: {result.score:.4f}):")
        print(result.payload.get('text', 'No text found'))
    print("\n")
    sys.exit(0)
except Exception as e:
    logger.exception("Error occurred during vector retrieval test run.")
    sys.exit(1)

