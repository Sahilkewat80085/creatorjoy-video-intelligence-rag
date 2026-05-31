import os
from apify_client import ApifyClient
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

apify_token = os.getenv("APIFY_API_TOKEN")
client = ApifyClient(apify_token)

run_input = {
    "startUrls": [{"url": "https://www.youtube.com/watch?v=0JlMjgqduVw"}],
    "maxResults": 1,
}

print("Running Apify youtube-scraper...")
run = client.actor("streamers/youtube-scraper").call(run_input=run_input)
dataset_id = run.default_dataset_id if hasattr(run, 'default_dataset_id') else run['defaultDatasetId']
items = list(client.dataset(dataset_id).iterate_items())

if items:
    print(items[0])
else:
    print("No items found.")
