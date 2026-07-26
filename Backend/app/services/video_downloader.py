import os
import uuid
import tempfile
import logging
import requests
import yt_dlp

logger = logging.getLogger(__name__)


class VideoDownloader:
    def __init__(self):
        """
        Initializes the VideoDownloader, setting the directory for temporary downloads.
        """
        self.temp_dir = tempfile.gettempdir()

    def download_youtube(self, url: str) -> str:
        """
        Downloads a YouTube video using yt-dlp and returns the path to the downloaded file.
        
        Args:
            url: The YouTube video URL.
            
        Returns:
            The path to the downloaded media file.
            
        Raises:
            Exception: If yt-dlp extraction or downloading fails.
        """
        video_id = str(uuid.uuid4())
        output_template = os.path.join(self.temp_dir, f"{video_id}.%(ext)s")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            logger.info("Starting yt-dlp download for URL: %s", url)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filepath = ydl.prepare_filename(info)
                
                # Check if the file exists; if not, check common extensions as yt-dlp can alter extension formats
                if not os.path.exists(filepath):
                    base = os.path.splitext(filepath)[0]
                    for ext in ['.mp4', '.mkv', '.webm']:
                        if os.path.exists(base + ext):
                            filepath = base + ext
                            break
                            
                logger.info("yt-dlp download successful: %s", filepath)
                return filepath
        except Exception as e:
            logger.exception("yt-dlp download failed for URL: %s", url)
            raise e

    def download_direct(self, url: str) -> str:
        """
        Downloads a video from a direct URL (e.g. Instagram Reels CDN URL) and returns the path.
        
        Args:
            url: The direct video URL.
            
        Returns:
            The path to the downloaded media file.
            
        Raises:
            Exception: If requests execution or file writing fails.
        """
        video_id = str(uuid.uuid4())
        filepath = os.path.join(self.temp_dir, f"{video_id}.mp4")
        
        try:
            logger.info("Starting direct download for URL: %s", url)
            # Added connection/read timeout (30 seconds) to prevent hanging requests in production
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info("Direct download successful: %s", filepath)
            return filepath
        except Exception as e:
            logger.exception("Direct download failed for URL: %s", url)
            raise e

    def cleanup(self, filepath: str):
        """
        Deletes the temporary file from the disk.
        
        Args:
            filepath: Path to the local file to clean up.
        """
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info("Cleaned up temporary file: %s", filepath)
            except Exception as e:
                logger.exception("Failed to clean up temporary file at path: %s", filepath)

