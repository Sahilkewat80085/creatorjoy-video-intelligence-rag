import sys
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import json

def test_youtube(url):
    print(f"Testing YouTube Extraction for URL: {url}")
    
    # Extract metadata using yt-dlp
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return
        
        video_id = info.get('id')
        print(f"Title: {info.get('title')}")
        print(f"Creator: {info.get('uploader')}")
        print(f"Views: {info.get('view_count')}")
        print(f"Likes: {info.get('like_count')}")
        print(f"Comments: {info.get('comment_count')}")
        print(f"Duration: {info.get('duration')} seconds")
    
    # Extract transcript
    print("\nAttempting to extract transcript...")
    subs = info.get('subtitles') or info.get('automatic_captions')
    if subs and 'en' in subs:
        print(f"Transcript available in English! Format: {subs['en'][0]['ext']}")
        print(f"Transcript URL: {subs['en'][0]['url']}")
    else:
        print("No English transcript found.")

if __name__ == "__main__":
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    test_youtube(test_url)
