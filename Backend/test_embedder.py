import sys
import logging
from app.services.embedder import EmbeddingService

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

try:
    logger.info("Initializing EmbeddingService (this may download the model if not cached)...")
    service = EmbeddingService()

    test_text = "Never gonna give you up, never gonna let you down."
    logger.info("Embedding text target: '%s'", test_text)

    vector = service.embed(test_text)

    logger.info("Embedding calculation complete.")
    print("\n--- Embedding Result ---")
    print(f"Vector length (dimensions): {len(vector)}")
    print(f"First 5 dimensions: {vector[:5]}")
    print("------------------------\n")
    sys.exit(0)
except Exception as e:
    logger.exception("Failed to initialize or execute embedding service.")
    sys.exit(1)

