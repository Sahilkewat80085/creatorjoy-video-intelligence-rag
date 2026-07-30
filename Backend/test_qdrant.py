import sys
import logging
from app.services.qdrant_store import QdrantStore

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

try:
    logger.info("Connecting to Qdrant cloud database...")
    store = QdrantStore()

    logger.info("Creating or resetting collection '%s' if it doesn't exist...", store.COLLECTION_NAME)
    store.create_collection()

    logger.info("Qdrant setup verified successfully!")
    sys.exit(0)
except Exception as e:
    logger.exception("Qdrant database setup verification failed.")
    sys.exit(1)

