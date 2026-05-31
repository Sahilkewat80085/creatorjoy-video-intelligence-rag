import requests

url = "http://localhost:8080/api/ingest"
data = {
  "video_a_url": "https://www.youtube.com/watch?v=0JlMjgqduVw",
  "video_b_url": "https://www.instagram.com/reels/DX4XJj9N8QH"
}
try:
    res = requests.post(url, json=data)
    print(res.status_code)
    print(res.text)
except Exception as e:
    print("Error:", e)
