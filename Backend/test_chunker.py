import sys
import logging
from app.services.chunker import TranscriptChunker
from app.providers.youtube_provider import YouTubeProvider

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

try:
    logger.info("Initializing YouTubeProvider to extract a test transcript...")
    provider = YouTubeProvider()
    video = provider.extract("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    long_transcript = video.transcript

    if not long_transcript:
        logger.error("Could not retrieve a valid transcript to run the test.")
        sys.exit(1)

    logger.info("Initializing TranscriptChunker and splitting transcript text...")
    chunker = TranscriptChunker()
    chunks = chunker.chunk(long_transcript)

    logger.info("Total chunks created: %d", len(chunks))

    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i} ---")
        print(chunk[:200])
        print("-----------------\n")
        
    sys.exit(0)
except Exception as e:
    logger.exception("Failed to execute chunker integration test.")
    sys.exit(1)

