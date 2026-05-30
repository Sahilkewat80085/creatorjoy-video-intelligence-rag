import sys
import os

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from app.services.chunker import TranscriptChunker
from app.providers.youtube_provider import YouTubeProvider

# Get a real transcript to test chunking
provider = YouTubeProvider()
video = provider.extract("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
long_transcript = video.transcript

if not long_transcript:
    print("Could not retrieve a transcript to test.")
    sys.exit(1)

chunker = TranscriptChunker()
chunks = chunker.chunk(long_transcript)

print(f"Total chunks created: {len(chunks)}")

for i, chunk in enumerate(chunks[:3]):
    print(f"\n--- Chunk {i} ---")
    print(chunk[:200])
