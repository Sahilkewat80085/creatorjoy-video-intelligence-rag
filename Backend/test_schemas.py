import sys
import json
import logging
from app.models.schemas import VideoData

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

try:
    logger.info("Initializing VideoData schema instance with test values...")
    video = VideoData(
        platform="youtube",
        video_id="123",
        source_url="https://youtube.com/watch?v=123",
        creator="MrBeast",
        views=1000,
        likes=100,
        comments=20,
    )
    
    logger.info("VideoData model successfully instantiated.")
    print("\n--- Schema Dump ---")
    print(json.dumps(video.model_dump(), indent=4))
    print("-------------------\n")
    sys.exit(0)
except Exception as e:
    logger.exception("Failed to validate schemas model execution.")
    sys.exit(1)

