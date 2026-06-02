import os
import requests
import uuid
import tempfile
import yt_dlp
import logging
import traceback

logger = logging.getLogger(__name__)

class VideoDownloader:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    def download_youtube(self, url: str) -> str:
        """Downloads YouTube video and returns the path to the downloaded file."""
        video_id = str(uuid.uuid4())
        output_template = os.path.join(self.temp_dir, f"{video_id}.%(ext)s")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            logger.info(f"[VideoDownloader] Starting yt-dlp download for {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filepath = ydl.prepare_filename(info)
                if not os.path.exists(filepath):
                    base = os.path.splitext(filepath)[0]
                    for ext in ['.mp4', '.mkv', '.webm']:
                        if os.path.exists(base + ext):
                            filepath = base + ext
                            break
                logger.info(f"[VideoDownloader] yt-dlp successful: {filepath}")
                return filepath
        except Exception as e:
            logger.error(f"[VideoDownloader Error] yt-dlp failed:\n{traceback.format_exc()}")
            raise e

    def download_direct(self, url: str) -> str:
        """Downloads a video from a direct URL (e.g. Instagram reel) and returns the path."""
        video_id = str(uuid.uuid4())
        filepath = os.path.join(self.temp_dir, f"{video_id}.mp4")
        
        try:
            logger.info(f"[VideoDownloader] Starting direct download for {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"[VideoDownloader] Direct download successful: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"[VideoDownloader Error] Direct download failed:\n{traceback.format_exc()}")
            raise e

    def cleanup(self, filepath: str):
        """Deletes the temporary file."""
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info(f"[VideoDownloader] Cleaned up {filepath}")
            except Exception as e:
                logger.error(f"[VideoDownloader Error] Failed to cleanup {filepath}:\n{traceback.format_exc()}")
