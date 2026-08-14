import os
import sys
import logging
from apify_client import ApifyClient
from dotenv import load_dotenv, find_dotenv

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(find_dotenv())


def test_apify_youtube() -> None:
    apify_token = os.getenv("APIFY_API_TOKEN", "").strip()
    if not apify_token:
        logger.error("APIFY_API_TOKEN environment variable is missing or empty.")
        sys.exit(1)
        
    try:
        logger.info("Initializing ApifyClient...")
        client = ApifyClient(apify_token)

        run_input = {
            "startUrls": [{"url": "https://www.youtube.com/watch?v=0JlMjgqduVw"}],
            "maxResults": 1,
        }

        logger.info("Invoking actor 'streamers/youtube-scraper' via Apify Client...")
        run = client.actor("streamers/youtube-scraper").call(run_input=run_input)
        
        dataset_id = getattr(run, 'default_dataset_id', getattr(run, 'defaultDatasetId', None))
        if not dataset_id:
            raise ValueError("Could not find default_dataset_id on Apify run result.")
            
        logger.info("Retrieving items from default dataset ID: %s", dataset_id)
        items = list(client.dataset(dataset_id).iterate_items())
        
        logger.info("Apify invocation complete. Returned items count: %d", len(items))
        if items:
            print("\n--- Scraped Item Metadata ---")
            print(items[0])
            print("-----------------------------\n")
        else:
            logger.warning("No items found in dataset.")
            
        sys.exit(0)
    except Exception as e:
        logger.exception("Failed to execute Apify client verification test.")
        sys.exit(1)


if __name__ == "__main__":
    test_apify_youtube()

