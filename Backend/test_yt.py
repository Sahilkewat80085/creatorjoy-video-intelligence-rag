import sys
import os
import logging

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.providers.youtube_provider import YouTubeProvider

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

try:
    logger.info("Initializing YouTubeProvider for simple verification check...")
    provider = YouTubeProvider()
    
    url = "https://www.youtube.com/watch?v=0JlMjgqduVw"
    logger.info("Extracting data for video: %s", url)
    video_data = provider.extract(url)
    
    logger.info("Extraction completed successfully.")
    logger.info("Views: %d, Creator: %s", video_data.views, video_data.creator)
    sys.exit(0)
except Exception as e:
    logger.exception("YouTube provider simple verification test failed.")
    sys.exit(1)

