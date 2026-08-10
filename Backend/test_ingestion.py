import sys
import os
import json
import logging
from dotenv import load_dotenv

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Load the env vars from project root
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

from app.services.ingestion_service import IngestionService

try:
    logger.info("Initializing IngestionService...")
    service = IngestionService()

    logger.info("Ingesting both YouTube and Instagram URLs...")
    result = service.ingest(
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        instagram_url="https://www.instagram.com/reels/DRuIVJyk0kU/"
    )

    logger.info("Ingestion completed successfully. Displaying results...")

    if "video_a" in result and result["video_a"]:
        print("\n--- YouTube Video Data (video_a) ---")
        yt_data = result["video_a"].model_dump()
        if yt_data.get('transcript') and len(yt_data['transcript']) > 150:
            yt_data['transcript'] = yt_data['transcript'][:150] + "... [TRUNCATED]"
        print(json.dumps(yt_data, indent=4))

    if "video_b" in result and result["video_b"]:
        print("\n--- Instagram Video Data (video_b) ---")
        print(json.dumps(result["video_b"].model_dump(), indent=4))
        print("--------------------------------------\n")
        
    sys.exit(0)
except Exception as e:
    logger.exception("Ingestion integration test run failed.")
    sys.exit(1)

