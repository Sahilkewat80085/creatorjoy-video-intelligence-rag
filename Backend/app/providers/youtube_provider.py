import os
import logging
from urllib.parse import urlparse, parse_qs
from apify_client import ApifyClient
from youtube_transcript_api import YouTubeTranscriptApi
from app.models.schemas import VideoData

logger = logging.getLogger(__name__)


class YouTubeProvider:
    def _extract_video_id(self, url: str) -> str:
        """
        Safely extracts the YouTube video ID from standard, mobile, embedded, or Shorts URLs.
        """
        try:
            parsed = urlparse(url)
            if parsed.hostname in ('youtu.be', 'www.youtu.be'):
                return parsed.path.lstrip('/')
            elif parsed.hostname in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
                query = parse_qs(parsed.query)
                video_id = query.get('v', [None])[0]
                if video_id:
                    return video_id
                
                # Check for embed or shorts path structures
                path_parts = parsed.path.strip('/').split('/')
                if len(path_parts) >= 2 and path_parts[0] in ('embed', 'shorts'):
                    return path_parts[1]
        except Exception:
            logger.warning("Fast URL parsing failed for URL: %s. Falling back to string splits.", url)
            
        # Fallback to string splits if urlparse fails or query parameter isn't found
        if "v=" in url:
            return url.split("v=")[-1].split("&")[0]
        return url.rstrip('/').split("/")[-1].split("?")[0]

    def extract(self, url: str) -> VideoData:
        """
        Extracts YouTube video metadata via Apify and fetches native english transcripts if available.
        
        Args:
            url: The YouTube video URL.
            
        Returns:
            A VideoData schema instance containing metadata and transcript.
            
        Raises:
            ValueError: If the APIFY_API_TOKEN is missing or Apify returns no data.
            Exception: If metadata extraction fails.
        """
        logger.info("Starting YouTube metadata and transcript extraction for URL: %s", url)
        
        video_id = self._extract_video_id(url)
        logger.info("Extracted YouTube video ID: %s", video_id)
        
        views, likes, comments, duration_sec = 0, 0, 0, 0
        creator = "YouTube Creator"
        
        apify_token = os.getenv("APIFY_API_TOKEN", "").strip()
        if not apify_token:
            logger.error("APIFY_API_TOKEN is missing or empty in environment variables.")
            raise ValueError("APIFY_API_TOKEN is missing or empty!")
            
        try:
            actor_id = "streamers/youtube-scraper"
            run_input = {
                "startUrls": [{"url": url}],
                "maxResults": 1,
            }
            logger.info("Invoking Apify actor '%s' with payload: %s", actor_id, run_input)
            
            client = ApifyClient(apify_token)
            run = client.actor(actor_id).call(run_input=run_input)
            
            run_id = getattr(run, 'id', 'UNKNOWN_RUN_ID')
            logger.info("Apify actor run triggered. Run ID: %s", run_id)
            
            dataset_id = getattr(run, 'default_dataset_id', getattr(run, 'defaultDatasetId', None))
            if not dataset_id:
                raise ValueError("Could not find default_dataset_id on Apify Run object.")
                
            items = list(client.dataset(dataset_id).iterate_items())
            logger.info("Retrieved %d raw response items from Apify dataset.", len(items))
            
            if items:
                item = items[0]
                video_id = item.get('id', video_id)
                views = item.get('viewCount', 0) or 0
                likes = item.get('likes', 0) or 0
                comments = item.get('commentsCount', 0) or 0
                creator = item.get('channelName') or creator
                
                # Parse duration "00:02:40"
                dur_str = item.get('duration')
                if dur_str:
                    parts = dur_str.split(':')
                    if len(parts) == 3:
                        duration_sec = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                    elif len(parts) == 2:
                        duration_sec = int(parts[0]) * 60 + int(parts[1])
                logger.info("Apify metadata extracted successfully. Views: %d, Creator: %s", views, creator)
            else:
                raise ValueError(f"Apify youtube-scraper returned no dataset items for URL {url}.")
                    
        except Exception as e:
            logger.exception("Apify YouTube metadata extraction failed.")
            raise e

        # Fetch native transcript
        transcript_text = ""
        transcript_source = None
        try:
            logger.info("Fetching native transcript for YouTube video: %s", video_id)
            api = YouTubeTranscriptApi()
            t_list = api.list(video_id)
            try:
                # Try manually created english transcript first
                transcript = t_list.find_transcript(['en'])
                logger.info("Found manual English transcript.")
            except Exception as e:
                logger.info("Manual English transcript not found (%s). Trying generated English transcript...", e)
                # Fallback to automatically generated english transcript
                transcript = t_list.find_generated_transcript(['en'])
                logger.info("Found generated English transcript.")
                
            raw_transcript = transcript.fetch()
            transcript_text = " ".join(
                [t.get('text', '') if isinstance(t, dict) else getattr(t, 'text', '') for t in raw_transcript]
            )
            
            if transcript_text:
                transcript_source = "native"
                logger.info("Native transcript fetch successful. Length: %d chars.", len(transcript_text))
                
        except Exception as e:
            logger.warning("Could not extract native transcript for video %s: %s", video_id, e)

        # Calculate engagement rate
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

