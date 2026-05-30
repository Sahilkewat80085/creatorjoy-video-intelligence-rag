import sys
import os
from dotenv import load_dotenv

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Load the env vars
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

from app.providers.instagram_provider import InstagramProvider
import json

provider = InstagramProvider()

print("Extracting Instagram reel...")
try:
    video = provider.extract("https://www.instagram.com/reels/DRuIVJyk0kU/")
    print("\n--- Final VideoData Result ---")
    print(json.dumps(video.model_dump(), indent=4))
except Exception as e:
    print(f"Extraction failed: {e}")
