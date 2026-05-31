import sys
import os
from dotenv import load_dotenv

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

from app.providers.youtube_provider import YouTubeProvider
from app.services.vector_pipeline import VectorPipeline

print("Extracting video data for testing pipeline...")
provider = YouTubeProvider()
video = provider.extract("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

print("Initializing VectorPipeline...")
pipeline = VectorPipeline()

pipeline.process_video(video)
print("Pipeline test complete.")
