import sys
import os
import json
import logging
from dotenv import load_dotenv
from apify_client import ApifyClient

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Load credentials from .env file explicitly
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)


def test_instagram_apify(url: str) -> None:
    logger.info("Testing Instagram Extraction for URL: %s using Apify", url)
    
    apify_token = os.getenv("APIFY_API_TOKEN", "").strip()
    if not apify_token:
        logger.error("APIFY_API_TOKEN not found in environment configuration.")
        sys.exit(1)

    try:
        logger.info("Initializing ApifyClient...")
        client = ApifyClient(apify_token)

        # Prepare the Actor input
        run_input = {
            "directUrls": [url],
            "resultsType": "details",
            "resultsLimit": 1,
            "searchType": "hashtag",
            "searchLimit": 1,
        }

        logger.info("Calling Apify Actor 'apify/instagram-scraper'...")
        run = client.actor("apify/instagram-scraper").call(run_input=run_input)

        logger.info("Actor run completed. Fetching results dataset...")
        items_found = 0
        
        dataset_id = getattr(run, 'default_dataset_id', getattr(run, 'defaultDatasetId', None))
        if not dataset_id:
            raise ValueError("Could not find default dataset ID in Apify run output.")
        
        for item in client.dataset(dataset_id).iterate_items():
            items_found += 1
            print(f"Creator: {item.get('ownerUsername')}")
            print(f"Creator Full Name: {item.get('ownerFullName')}")
            print(f"Creator Followers: {item.get('ownerFollowersCount', 'Not in this payload (requires profile scrape)')}")
            print(f"Caption: {item.get('caption', 'None')}")
            print(f"Likes: {item.get('likesCount')}")
            print(f"Comments: {item.get('commentsCount')}")
            print(f"Views: {item.get('videoViewCount')}")
            print(f"Hashtags: {item.get('hashtags')}")
            print(f"Type: {item.get('type')}")
            
            # Print raw JSON snippet for debugging
            raw_snippet = json.dumps(item, indent=2)[:500]
            print(f"\nRaw Data Snippet:\n{raw_snippet}...\n")
            
        if items_found == 0:
            logger.warning("No items found. The URL might be private, invalid, or rate-limited.")
            sys.exit(1)
            
        logger.info("Instagram extraction verification test complete.")
        sys.exit(0)

    except Exception as e:
        logger.exception("Error extracting Instagram data via Apify.")
        sys.exit(1)


if __name__ == "__main__":
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.instagram.com/reel/C8qLZZmP4O-/"
    test_instagram_apify(test_url)

