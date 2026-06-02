import os
import requests
import uuid
import tempfile
import yt_dlp

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
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # the exact filename might differ slightly due to merging, but ydl handles it
                filepath = ydl.prepare_filename(info)
                # If the extension changed after merging (e.g., .webm), we check the file
                if not os.path.exists(filepath):
                    # Sometimes yt-dlp renames it after merging, so we find the base name
                    base = os.path.splitext(filepath)[0]
                    for ext in ['.mp4', '.mkv', '.webm']:
                        if os.path.exists(base + ext):
                            return base + ext
                return filepath
        except Exception as e:
            print(f"Error downloading YouTube video: {e}")
            raise e

    def download_direct(self, url: str) -> str:
        """Downloads a video from a direct URL (e.g. Instagram reel) and returns the path."""
        video_id = str(uuid.uuid4())
        filepath = os.path.join(self.temp_dir, f"{video_id}.mp4")
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filepath
        except Exception as e:
            print(f"Error downloading direct video URL: {e}")
            raise e

    def cleanup(self, filepath: str):
        """Deletes the temporary file."""
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Failed to cleanup {filepath}: {e}")
