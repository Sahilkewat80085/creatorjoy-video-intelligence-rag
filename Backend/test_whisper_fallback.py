import asyncio
from app.services.ingestion_service import IngestionService
from dotenv import load_dotenv

load_dotenv()

def test_ingestion():
    ingestion_service = IngestionService()
    
    youtube_native = "https://www.youtube.com/watch?v=jNQXAC9IVRw" # Me at the zoo, has native transcript
    youtube_no_native = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Rick Roll, often CC disabled or we can just mock it.
    
    print("\n=== Testing YouTube without Native Transcript ===")
    try:
        vid_no = ingestion_service.youtube_provider.extract(youtube_no_native)
        # Force transcript to be None to guarantee fallback triggers even if it has auto-subs
        vid_no.transcript = None
        vid_no = ingestion_service._apply_whisper_fallback(vid_no)
        print(f"Source: {vid_no.transcript_source}")
        print(f"Has transcript: {bool(vid_no.transcript)}")
        if vid_no.transcript:
            print(f"Transcript Snippet: {vid_no.transcript[:100]}...")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_ingestion()
