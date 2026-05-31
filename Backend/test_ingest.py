import requests

url = "http://localhost:8080/api/ingest"
data = {
  "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "instagram_url": "https://www.instagram.com/reels/DYGZgr5IfaN/"
}

r = requests.post(url, json=data)
print(r.status_code)
print(r.json())
