import sys
import os
from dotenv import load_dotenv

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Load the env vars from project root
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

from app.services.ingestion_service import IngestionService
import json

service = IngestionService()

print("Ingesting both YouTube and Instagram URLs...")
result = service.ingest(
    youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    instagram_url="https://www.instagram.com/reels/DRuIVJyk0kU/"
)

print("\n--- YouTube Video Data (video_a) ---")
yt_data = result["video_a"].model_dump()
if yt_data.get('transcript') and len(yt_data['transcript']) > 150:
    yt_data['transcript'] = yt_data['transcript'][:150] + "... [TRUNCATED]"
print(json.dumps(yt_data, indent=4))

print("\n--- Instagram Video Data (video_b) ---")
print(json.dumps(result["video_b"].model_dump(), indent=4))
