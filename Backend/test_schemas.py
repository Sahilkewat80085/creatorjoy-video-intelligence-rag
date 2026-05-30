from app.models.schemas import VideoData

video = VideoData(
    platform="youtube",
    video_id="123",
    source_url="https://youtube.com/watch?v=123",
    creator="MrBeast",
    views=1000,
    likes=100,
    comments=20,
)

print(video.model_dump())
