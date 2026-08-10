import sys
import json
import logging
from dotenv import load_dotenv

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Load the env vars
load_dotenv()

from app.providers.youtube_provider import YouTubeProvider

try:
    logger.info("Initializing YouTubeProvider...")
    provider = YouTubeProvider()

    logger.info("Extracting YouTube video metadata and transcript...")
    video = provider.extract("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    data = video.model_dump()

    # Truncate transcript for cleaner console output
    if data.get('transcript') and len(data['transcript']) > 200:
        data['transcript'] = data['transcript'][:200] + "... [TRUNCATED]"

    logger.info("YouTube extraction completed successfully.")
    print("\n--- Final VideoData Result ---")
    print(json.dumps(data, indent=4))
    print("------------------------------\n")
    sys.exit(0)
except Exception as e:
    logger.exception("YouTube provider extraction test failed.")
    sys.exit(1)

