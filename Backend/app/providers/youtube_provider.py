import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from app.models.schemas import VideoData

class YouTubeProvider:

    def extract(self, url: str) -> VideoData:
        # get metadata
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            video_id = info.get('id', '')
            views = info.get('view_count', 0) or 0
            likes = info.get('like_count', 0) or 0
            comments = info.get('comment_count', 0) or 0
            duration = info.get('duration', 0) or 0
            creator = info.get('uploader') or info.get('channel') or "Unknown"

        # get transcript
        transcript_text = ""
        try:
            api = YouTubeTranscriptApi()
            t_list = api.list(video_id)
            try:
                # Try manually created english transcript first
                transcript = t_list.find_transcript(['en'])
            except:
                # Fallback to automatically generated english transcript
                transcript = t_list.find_generated_transcript(['en'])
                
            raw_transcript = transcript.fetch()
            # Handle both dictionary and object formats depending on youtube_transcript_api version
            transcript_text = " ".join(
                [t.get('text', '') if isinstance(t, dict) else getattr(t, 'text', '') for t in raw_transcript]
            )
        except Exception as e:
            print(f"Warning: Could not extract transcript: {e}")

        # calculate engagement
        engagement_rate = 0.0
        if views > 0:
            engagement_rate = ((likes + comments) / views) * 100

        return VideoData(
            platform="youtube",
            video_id=video_id,
            source_url=url,
            creator=creator,
            views=views,
            likes=likes,
            comments=comments,
            engagement_rate=round(engagement_rate, 2),
            transcript=transcript_text,
            duration=duration
        )
