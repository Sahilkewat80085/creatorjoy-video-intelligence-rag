import logging
from typing import Dict
from app.providers.youtube_provider import YouTubeProvider
from app.providers.instagram_provider import InstagramProvider
from app.services.video_downloader import VideoDownloader
from app.services.audio_extractor import AudioExtractor
from app.services.transcription_service import TranscriptionService
from app.models.schemas import VideoData

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self):
        """
        Initializes the IngestionService with providers, downloader, extractor, and transcriber.
        """
        self.youtube_provider = YouTubeProvider()
        self.instagram_provider = InstagramProvider()
        self.downloader = VideoDownloader()
        self.extractor = AudioExtractor()
        self.transcriber = TranscriptionService()

    def _apply_whisper_fallback(self, video: VideoData) -> VideoData:
        """
        Attempts to download and transcribe the video using Whisper if native transcript is missing.
        
        Args:
            video: The VideoData schema object.
            
        Returns:
            The updated VideoData schema object with transcript fields if successful.
        """
        if video.transcript:
            logger.info("Native transcript found for %s video %s", video.platform, video.video_id)
            return video

        if not video.direct_media_url:
            logger.warning("No native transcript and no direct media URL available for %s video %s", video.platform, video.video_id)
            video.transcript_source = "unavailable"
            return video

        logger.info("Falling back to Whisper transcription for %s video %s", video.platform, video.video_id)
        video_path = None
        audio_path = None
        try:
            # 1. Download Video
            if video.platform == "youtube":
                video_path = self.downloader.download_youtube(video.direct_media_url)
            else:
                video_path = self.downloader.download_direct(video.direct_media_url)

            # 2. Extract Audio
            audio_path = self.extractor.extract_audio(video_path)

            # 3. Transcribe
            result = self.transcriber.transcribe_video(audio_path)
            
            video.transcript = result.get("transcript")
            video.transcript_source = result.get("source")
            logger.info("Whisper transcription successfully completed for video %s", video.video_id)
        except Exception as e:
            logger.exception("Whisper fallback transcription failed for video %s", video.video_id)
            video.transcript_source = "unavailable"
        finally:
            # 4. Cleanup downloaded temporary files
            if video_path:
                self.downloader.cleanup(video_path)
            if audio_path:
                self.downloader.cleanup(audio_path)
            
        return video

    def ingest(self, youtube_url: str, instagram_url: str) -> Dict[str, VideoData]:
        """
        Ingests video data from both a YouTube URL and an Instagram URL.
        Downloads and transcribes them if necessary.
        
        Args:
            youtube_url: The URL of the YouTube video.
            instagram_url: The URL of the Instagram Reel.
            
        Returns:
            A dictionary containing processed VideoData for both videos.
        """
        logger.info("Starting ingestion workflow for YouTube: %s and Instagram: %s", youtube_url, instagram_url)
        
        video_a = self.youtube_provider.extract(youtube_url)
        if video_a:
            video_a = self._apply_whisper_fallback(video_a)
        else:
            logger.error("Failed to extract video data from YouTube URL: %s", youtube_url)

        video_b = self.instagram_provider.extract(instagram_url)
        if video_b:
            video_b = self._apply_whisper_fallback(video_b)
        else:
            logger.error("Failed to extract video data from Instagram URL: %s", instagram_url)

        return {
            "video_a": video_a,
            "video_b": video_b
        }

