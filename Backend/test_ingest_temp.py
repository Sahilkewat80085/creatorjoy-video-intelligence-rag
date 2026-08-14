import sys
import logging
import requests

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

url = "http://localhost:8080/api/ingest"
data = {
    "video_a_url": "https://www.youtube.com/watch?v=0JlMjgqduVw",
    "video_b_url": "https://www.instagram.com/reels/DX4XJj9N8QH"
}

try:
    logger.info("Sending ingestion request to temporary validation endpoint: %s", url)
    
    # timeout=(5, 45) sets connection timeout to 5 seconds and read timeout to 45 seconds
    res = requests.post(url, json=data, timeout=(5, 45))
    
    logger.info("Response Status Code: %d", res.status_code)
    print("\n--- Temp Ingest Response ---")
    print(res.text)
    print("----------------------------\n")
    
    res.raise_for_status()
    sys.exit(0)
except Exception as e:
    logger.exception("Temporary ingestion test request failed.")
    sys.exit(1)

