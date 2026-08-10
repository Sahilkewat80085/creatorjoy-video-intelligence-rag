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

# Load the env vars
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

from app.providers.instagram_provider import InstagramProvider

try:
    logger.info("Initializing InstagramProvider...")
    provider = InstagramProvider()

    logger.info("Extracting Instagram reel data...")
    video = provider.extract("https://www.instagram.com/reels/DRuIVJyk0kU/")
    
    logger.info("Instagram extraction completed successfully.")
    print("\n--- Final VideoData Result ---")
    print(json.dumps(video.model_dump(), indent=4))
    print("------------------------------\n")
    sys.exit(0)
except Exception as e:
    logger.exception("Instagram provider extraction test failed.")
    sys.exit(1)

