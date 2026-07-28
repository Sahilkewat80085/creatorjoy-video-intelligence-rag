import os
import logging
from urllib.parse import urlparse
from apify_client import ApifyClient
from app.models.schemas import VideoData

logger = logging.getLogger(__name__)


class InstagramProvider:
    def _extract_shortcode(self, url: str) -> str:
        """
        Safely extracts the Instagram shortcode from Reel, post, or standard media URLs.
        """
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2 and path_parts[0] in ('p', 'reel', 'reels', 'tv'):
                return path_parts[1]
            if path_parts:
                return path_parts[-1]
        except Exception:
            logger.warning("URL parsing failed for Instagram URL: %s. Falling back to string splits.", url)
            
        shortcode = url.rstrip('/').split('/')[-1]
        if '?' in shortcode:
            shortcode = shortcode.split('?')[0]
        return shortcode

    def extract(self, url: str) -> VideoData:
        """
        Extracts Instagram Reel metadata via Apify scraper.
        
        Args:
            url: The Instagram Reel/post URL.
            
        Returns:
            A VideoData schema instance containing media metadata.
            
        Raises:
            ValueError: If APIFY_API_TOKEN is missing or Apify dataset contains no items/errors.
            Exception: If the extraction execution fails.
        """
        logger.info("Starting Instagram metadata extraction for URL: %s", url)
        
        apify_token = os.getenv("APIFY_API_TOKEN", "").strip()
        if not apify_token:
            err_msg = "APIFY_API_TOKEN is missing from environment variables."
            logger.error(err_msg)
            raise ValueError(err_msg)

        shortcode = self._extract_shortcode(url)
        logger.info("Extracted Instagram shortcode: %s", shortcode)

        try:
            client = ApifyClient(apify_token)

            run_input = {
                "directUrls": [url],
                "resultsType": "details",
                "resultsLimit": 1,
                "searchType": "hashtag",
                "searchLimit": 1,
            }

            logger.info("Calling Apify actor 'apify/instagram-scraper' for shortcode %s...", shortcode)
            run = client.actor("apify/instagram-scraper").call(run_input=run_input)
            
            run_id = getattr(run, 'id', 'UNKNOWN_RUN_ID')
            logger.info("Apify Instagram actor completed run. Run ID: %s", run_id)
            
            dataset_id = getattr(run, 'default_dataset_id', getattr(run, 'defaultDatasetId', None))
            if not dataset_id:
                raise ValueError("Could not find default_dataset_id on Apify Run object.")
                
            items = list(client.dataset(dataset_id).iterate_items())
            logger.info("Retrieved %d raw items from Apify dataset.", len(items))
            
            if not items:
                raise ValueError(f"No dataset items returned by Apify scraper for URL: {url}")
                
            item = items[0]
            
            # Check for errors in the payload returned by scraper
            if item.get("error"):
                raise ValueError(f"Apify Scraper Error: {item.get('errorDescription', item.get('error'))}")
                
            creator_username = item.get("ownerUsername") or ""
            creator_full_name = item.get("ownerFullName")
            views = item.get("videoViewCount") or 0
            likes = item.get("likesCount") or 0
            comments = item.get("commentsCount") or 0
            caption = item.get("caption")
            hashtags = item.get("hashtags") or []
            
            engagement_rate = 0.0
            if views > 0:
                engagement_rate = ((likes + comments) / views) * 100
                
            direct_media_url = item.get("videoUrl")
            logger.info("Instagram metadata successfully extracted for shortcode %s.", shortcode)
                
            return VideoData(
                platform="instagram",
                video_id=shortcode,
                source_url=url,
                creator=creator_username,
                creator_name=creator_full_name,
                views=views,
                likes=likes,
                comments=comments,
                engagement_rate=round(engagement_rate, 2),
                hashtags=hashtags,
                caption=caption,
                transcript=None,
                transcript_source=None,
                direct_media_url=direct_media_url,
                duration=None
            )
        except Exception as e:
            logger.exception("Failed to extract metadata for Instagram URL: %s", url)
            raise e

