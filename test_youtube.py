import sys
import logging
import yt_dlp

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def test_youtube(url: str) -> None:
    logger.info("Testing YouTube Extraction for URL: %s", url)
    
    ydl_opts = {'quiet': True}
    try:
        logger.info("Extracting metadata using yt_dlp...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        if not info:
            raise ValueError("No video information returned from yt_dlp extraction.")

        logger.info("Metadata extraction completed successfully.")
        print(f"Title: {info.get('title')}")
        print(f"Creator: {info.get('uploader')}")
        print(f"Views: {info.get('view_count')}")
        print(f"Likes: {info.get('like_count')}")
        print(f"Comments: {info.get('comment_count')}")
        print(f"Duration: {info.get('duration')} seconds")
        
        logger.info("Checking English transcripts and captions availability...")
        subs = info.get('subtitles') or info.get('automatic_captions')
        if subs and 'en' in subs:
            logger.info("English transcript/caption format: %s", subs['en'][0]['ext'])
            logger.info("Transcript URL: %s", subs['en'][0]['url'])
        else:
            logger.warning("No English transcript/caption entries found in metadata.")
            
        sys.exit(0)
    except Exception as e:
        logger.exception("Failed to verify YouTube metadata extraction.")
        sys.exit(1)


if __name__ == "__main__":
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    test_youtube(test_url)

