from app.providers.youtube_provider import YouTubeProvider
from app.providers.instagram_provider import InstagramProvider
from app.services.video_downloader import VideoDownloader
from app.services.audio_extractor import AudioExtractor
from app.services.transcription_service import TranscriptionService
from app.models.schemas import VideoData

class IngestionService:

    def __init__(self):
        self.youtube_provider = YouTubeProvider()
        self.instagram_provider = InstagramProvider()
        self.downloader = VideoDownloader()
        self.extractor = AudioExtractor()
        self.transcriber = TranscriptionService()

    def _apply_whisper_fallback(self, video: VideoData) -> VideoData:
        """Attempts to download and transcribe the video using Whisper if native transcript is missing."""
        if video.transcript:
            print(f"[TRANSCRIPT] Native transcript found for {video.platform} video {video.video_id}")
            return video

        if not video.direct_media_url:
            print(f"[TRANSCRIPT] No native transcript and no direct media URL for {video.video_id}")
            video.transcript_source = "unavailable"
            return video

        print(f"[TRANSCRIPT] Falling back to Whisper for {video.platform} video {video.video_id}")
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
            
        except Exception as e:
            print(f"Whisper fallback failed for {video.video_id}: {e}")
            video.transcript_source = "unavailable"
        finally:
            # 4. Cleanup
            self.downloader.cleanup(video_path)
            self.downloader.cleanup(audio_path)
            
        return video

    def ingest(
        self,
        youtube_url: str,
        instagram_url: str
    ):
        video_a = self.youtube_provider.extract(youtube_url)
        video_a = self._apply_whisper_fallback(video_a)

        video_b = self.instagram_provider.extract(instagram_url)
        video_b = self._apply_whisper_fallback(video_b)

        return {
            "video_a": video_a,
            "video_b": video_b
        }
