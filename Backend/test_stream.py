import sys
import logging
import requests

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

url = "http://localhost:8080/api/chat/stream"
data = {
    "session_id": "demo",
    "question": "Who is the creator of Video B?"
}

try:
    logger.info("Sending post request to streaming endpoint: %s", url)
    
    # timeout=(5, 30) sets a connection timeout of 5 seconds and a read timeout of 30 seconds
    with requests.post(url, json=data, stream=True, timeout=(5, 30)) as r:
        r.raise_for_status()
        logger.info("Connection established, streaming response tokens:")
        
        for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                sys.stdout.write(chunk)
                sys.stdout.flush()
                
    print("\n")
    logger.info("Stream finished successfully.")
    sys.exit(0)
except Exception as e:
    logger.exception("Error occurred while executing stream response test.")
    sys.exit(1)

