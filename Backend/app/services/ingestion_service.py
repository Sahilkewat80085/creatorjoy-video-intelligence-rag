from app.providers.youtube_provider import YouTubeProvider
from app.providers.instagram_provider import InstagramProvider


class IngestionService:

    def __init__(self):
        self.youtube_provider = YouTubeProvider()
        self.instagram_provider = InstagramProvider()

    def ingest(
        self,
        youtube_url: str,
        instagram_url: str
    ):

        video_a = self.youtube_provider.extract(youtube_url)

        video_b = self.instagram_provider.extract(instagram_url)

        return {
            "video_a": video_a,
            "video_b": video_b
        }
