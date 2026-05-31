import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.providers.youtube_provider import YouTubeProvider

provider = YouTubeProvider()
video_data = provider.extract("https://www.youtube.com/watch?v=0JlMjgqduVw")
print(f"Views: {video_data.views}, Creator: {video_data.creator}")
