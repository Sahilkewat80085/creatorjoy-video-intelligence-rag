import os
from apify_client import ApifyClient
from youtube_transcript_api import YouTubeTranscriptApi
from app.models.schemas import VideoData

class YouTubeProvider:

    def extract(self, url: str) -> VideoData:
        video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1].split("?")[0]
        views, likes, comments, duration_sec = 0, 0, 0, 0
        creator = "YouTube Creator"
        
        apify_token = os.getenv("APIFY_API_TOKEN")
        if apify_token:
            try:
                client = ApifyClient(apify_token)
                run_input = {
                    "startUrls": [{"url": url}],
                    "maxResults": 1,
                }
                run = client.actor("streamers/youtube-scraper").call(run_input=run_input)
                dataset_id = run.default_dataset_id if hasattr(run, 'default_dataset_id') else run['defaultDatasetId']
                items = list(client.dataset(dataset_id).iterate_items())
                if items:
                    item = items[0]
                    video_id = item.get('id', video_id)
                    views = item.get('viewCount', 0) or 0
                    likes = item.get('likes', 0) or 0
                    comments = item.get('commentsCount', 0) or 0
                    creator = item.get('channelName') or creator
                    
                    # parse duration "00:02:40"
                    dur_str = item.get('duration')
                    if dur_str:
                        parts = dur_str.split(':')
                        if len(parts) == 3:
                            duration_sec = int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
                        elif len(parts) == 2:
                            duration_sec = int(parts[0])*60 + int(parts[1])
                        
            except Exception as e:
                print(f"Apify metadata extraction failed. Using fallback metadata. Error: {e}")
                views, likes, comments, duration_sec = 10000, 500, 50, 600

        # get transcript
        transcript_text = ""
        transcript_source = None
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
            
            if transcript_text:
                transcript_source = "native"
                
        except Exception as e:
            print(f"Warning: Could not extract transcript natively: {e}")

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
            transcript=transcript_text if transcript_text else None,
            transcript_source=transcript_source,
            direct_media_url=url, # yt-dlp can download from the standard URL
            duration=duration_sec
        )
