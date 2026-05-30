import os
from apify_client import ApifyClient
from app.models.schemas import VideoData

class InstagramProvider:
    def extract(self, url: str) -> VideoData:
        apify_token = os.getenv("APIFY_API_TOKEN")
        if not apify_token:
            raise ValueError("APIFY_API_TOKEN is missing from environment variables.")

        client = ApifyClient(apify_token)

        run_input = {
            "directUrls": [url],
            "resultsType": "details",
            "resultsLimit": 1,
            "searchType": "hashtag",
            "searchLimit": 1,
        }

        # Run the Apify actor
        run = client.actor("apify/instagram-scraper").call(run_input=run_input)
        
        dataset_id = run.default_dataset_id if hasattr(run, 'default_dataset_id') else run['defaultDatasetId']
        items = list(client.dataset(dataset_id).iterate_items())
        
        if not items:
            raise ValueError(f"No data found for URL: {url}")
            
        item = items[0]
        
        # Check for errors in the payload
        if item.get("error"):
            raise ValueError(f"Apify Error: {item.get('errorDescription', item.get('error'))}")
            
        shortcode = url.rstrip('/').split('/')[-1]
        if '?' in shortcode:
            shortcode = shortcode.split('?')[0]
        
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
            duration=None
        )
