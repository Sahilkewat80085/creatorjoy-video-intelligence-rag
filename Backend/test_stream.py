import requests
import sys

url = "http://localhost:8080/api/chat/stream"
data = {
    "session_id": "demo",
    "question": "Who is the creator of Video B?"
}

print("Starting request...")
with requests.post(url, json=data, stream=True) as r:
    for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            sys.stdout.write(chunk)
            sys.stdout.flush()
print("\nStream finished.")
