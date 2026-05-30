import sys
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
import os
from dotenv import load_dotenv
from apify_client import ApifyClient
import json

# Load credentials from .env file explicitly
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

def test_instagram_apify(url):
    print(f"Testing Instagram Extraction for URL: {url} using Apify")
    
    apify_token = os.getenv("APIFY_API_TOKEN")
    
    if not apify_token:
        print("Error: APIFY_API_TOKEN not found in .env file.")
        return

    # Initialize the ApifyClient with your API token
    client = ApifyClient(apify_token)

    # Prepare the Actor input
    run_input = {
        "directUrls": [url],
        "resultsType": "details",
        "resultsLimit": 1,
        "searchType": "hashtag",
        "searchLimit": 1,
    }

    print("Calling Apify Actor (this might take a few seconds)...")
    try:
        # Run the Actor (we use a popular instagram scraper)
        # Using apify/instagram-scraper which is the most standard
        run = client.actor("apify/instagram-scraper").call(run_input=run_input)

        # Fetch and print Actor results from the run's dataset
        print("\n--- Apify Results ---")
        items_found = 0
        
        # Determine dataset ID based on apify-client version
        dataset_id = run.default_dataset_id if hasattr(run, 'default_dataset_id') else run['defaultDatasetId']
        
        for item in client.dataset(dataset_id).iterate_items():
            items_found += 1
            print(f"Creator: {item.get('ownerUsername')}")
            print(f"Creator Full Name: {item.get('ownerFullName')}")
            # Follower count might be returned if we scrape profile, let's see if post data has it
            print(f"Creator Followers: {item.get('ownerFollowersCount', 'Not in this payload (requires profile scrape)')}")
            print(f"Caption: {item.get('caption', 'None')}")
            print(f"Likes: {item.get('likesCount')}")
            print(f"Comments: {item.get('commentsCount')}")
            print(f"Views: {item.get('videoViewCount')}")
            print(f"Hashtags: {item.get('hashtags')}")
            print(f"Type: {item.get('type')}")
            
            # Print raw JSON for debugging
            print("\nRaw Data Snippet:")
            print(json.dumps(item, indent=2)[:500] + "...\n")
            
        if items_found == 0:
            print("No items found. The URL might be private or invalid.")

    except Exception as e:
        print(f"Error extracting Instagram data via Apify: {e}")

if __name__ == "__main__":
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.instagram.com/reel/C8qLZZmP4O-/"
    test_instagram_apify(test_url)
