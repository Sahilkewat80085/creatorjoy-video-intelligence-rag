import sys
import logging
from app.services.ingestion_service import IngestionService
from dotenv import load_dotenv

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Load the env vars
load_dotenv()


def test_ingestion() -> None:
    try:
        logger.info("Initializing IngestionService for whisper fallback test...")
        ingestion_service = IngestionService()
        
        youtube_no_native = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        logger.info("Extracting metadata for video (YouTube ID): %s", youtube_no_native)
        vid_no = ingestion_service.youtube_provider.extract(youtube_no_native)
        
        logger.info("Forcing transcript to None to test Whisper model fallback execution...")
        vid_no.transcript = None
        vid_no.transcript_source = None
        
        logger.info("Applying Whisper local audio extraction and speech-to-text fallback...")
        vid_no = ingestion_service._apply_whisper_fallback(vid_no)
        
        logger.info("Whisper processing completed successfully.")
        logger.info("Transcript Source: %s", vid_no.transcript_source)
        logger.info("Has transcript content: %s", bool(vid_no.transcript))
        
        if vid_no.transcript:
            logger.info("Transcript Snippet: %s...", vid_no.transcript[:150])
            
        sys.exit(0)
    except Exception as e:
        logger.exception("Whisper fallback integration test crashed.")
        sys.exit(1)


if __name__ == "__main__":
    test_ingestion()

