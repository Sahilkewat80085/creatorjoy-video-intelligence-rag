import os
from apify_client import ApifyClient
from youtube_transcript_api import YouTubeTranscriptApi
from app.models.schemas import VideoData

class YouTubeProvider:

    def extract(self, url: str) -> VideoData:
        import traceback
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"[YouTube Extractor] Starting extraction for URL: {url}")
        
        video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1].split("?")[0]
        views, likes, comments, duration_sec = 0, 0, 0, 0
        creator = "YouTube Creator"
        
        apify_token = os.getenv("APIFY_API_TOKEN", "").strip()
        if not apify_token:
            logger.error("[YouTube Extractor Error] APIFY_API_TOKEN is missing or empty!")
            raise ValueError("APIFY_API_TOKEN is missing or empty!")
        else:
            try:
                actor_id = "streamers/youtube-scraper"
                run_input = {
                    "startUrls": [{"url": url}],
                    "maxResults": 1,
                }
                logger.info(f"[YouTube Extractor] Calling Apify actor: {actor_id}")
                logger.info(f"[YouTube Extractor] Input payload: {run_input}")
                
                client = ApifyClient(apify_token)
                run = client.actor(actor_id).call(run_input=run_input)
                
                logger.info(f"[YouTube Extractor] Apify run object type: {type(run)}")
                logger.info(f"[YouTube Extractor] Apify run object: {run}")
                
                run_id = getattr(run, 'id', 'UNKNOWN_RUN_ID')
                logger.info(f"[YouTube Extractor] Apify actor invoked successfully. Run ID: {run_id}")
                
                dataset_id = getattr(run, 'default_dataset_id', getattr(run, 'defaultDatasetId', None))
                if not dataset_id:
                    raise ValueError("Could not find default_dataset_id on Run object")
                    
                items = list(client.dataset(dataset_id).iterate_items())
                
                logger.info(f"[YouTube Extractor] Raw Apify response items count: {len(items)}")
                
                if items:
                    item = items[0]
                    logger.info(f"[YouTube Extractor] Raw Apify item: {item}")
                    
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
                    logger.info(f"[YouTube Extractor] Apify metadata successful: views={views}, creator={creator}")
                else:
                    logger.error("[YouTube Extractor Error] Apify returned 0 items.")
                    raise ValueError(f"Apify youtube-scraper returned no data for {url}")
                        
            except Exception as e:
                logger.error(f"[YouTube Extractor Error] Apify metadata extraction failed:\n{traceback.format_exc()}")
                raise e # Re-raise to fail the request explicitly

        # get transcript
        transcript_text = ""
        transcript_source = None
        try:
            logger.info(f"[YouTube Extractor] Fetching native transcript for {video_id}")
            api = YouTubeTranscriptApi()
            t_list = api.list(video_id)
            try:
                # Try manually created english transcript first
                transcript = t_list.find_transcript(['en'])
            except Exception as e:
                logger.info(f"[YouTube Extractor] Manual transcript not found, trying generated: {e}")
                # Fallback to automatically generated english transcript
                transcript = t_list.find_generated_transcript(['en'])
                
            raw_transcript = transcript.fetch()
            # Handle both dictionary and object formats depending on youtube_transcript_api version
            transcript_text = " ".join(
                [t.get('text', '') if isinstance(t, dict) else getattr(t, 'text', '') for t in raw_transcript]
            )
            
            if transcript_text:
                transcript_source = "native"
                logger.info(f"[YouTube Extractor] Native transcript fetch successful! Length: {len(transcript_text)}")
                
        except Exception as e:
            logger.error(f"[YouTube Extractor Error] Could not extract transcript natively:\n{traceback.format_exc()}")

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
