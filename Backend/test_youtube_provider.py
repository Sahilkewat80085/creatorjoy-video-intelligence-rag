import sys
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from app.providers.youtube_provider import YouTubeProvider
import json
from dotenv import load_dotenv
load_dotenv()

provider = YouTubeProvider()

print("Extracting YouTube video...")
video = provider.extract("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

data = video.model_dump()

# Truncate transcript for cleaner console output
if data.get('transcript') and len(data['transcript']) > 200:
    data['transcript'] = data['transcript'][:200] + "... [TRUNCATED]"

print("\n--- Final VideoData Result ---")
print(json.dumps(data, indent=4))
