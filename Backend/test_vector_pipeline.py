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

from app.providers.youtube_provider import YouTubeProvider
from app.services.vector_pipeline import VectorPipeline

try:
    logger.info("Extracting video data for testing pipeline...")
    provider = YouTubeProvider()
    video = provider.extract("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    logger.info("Initializing VectorPipeline...")
    pipeline = VectorPipeline()
    
    pipeline.process_video(video)
    logger.info("Pipeline test complete successfully.")
except Exception as e:
    logger.exception("Pipeline test execution failed.")
    sys.exit(1)

