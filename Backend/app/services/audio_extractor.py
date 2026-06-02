import os
import subprocess
import imageio_ffmpeg

class AudioExtractor:
    def extract_audio(self, video_path: str) -> str:
        """
        Extracts audio from a video file and saves it as a .wav file.
        Uses the ffmpeg executable provided by imageio_ffmpeg.
        Returns the path to the extracted .wav file.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        base_path, _ = os.path.splitext(video_path)
        audio_path = f"{base_path}.wav"
        
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Extract audio as 16kHz mono WAV (ideal for Whisper)
        command = [
            ffmpeg_exe,
            "-i", video_path,
            "-vn",          # Disable video
            "-acodec", "pcm_s16le",
            "-ar", "16000", # 16kHz sample rate
            "-ac", "1",     # Mono
            "-y",           # Overwrite output
            audio_path
        ]
        
        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return audio_path
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio with ffmpeg: {e}")
            raise e
