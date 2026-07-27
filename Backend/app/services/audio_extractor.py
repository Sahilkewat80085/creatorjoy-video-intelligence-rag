import os
import subprocess
import logging
import imageio_ffmpeg

logger = logging.getLogger(__name__)


class AudioExtractor:
    def extract_audio(self, video_path: str) -> str:
        """
        Extracts audio from a video file and saves it as a 16kHz mono PCM .wav file (optimized for Whisper).
        Uses the ffmpeg executable provided by imageio_ffmpeg.
        
        Args:
            video_path: The absolute or relative path to the local video file.
            
        Returns:
            The path to the extracted .wav file.
            
        Raises:
            FileNotFoundError: If the input video path does not exist or is not a file.
            subprocess.CalledProcessError: If the ffmpeg subprocess execution fails.
        """
        if not video_path:
            raise ValueError("Input video path cannot be empty.")

        if not os.path.exists(video_path) or not os.path.isfile(video_path):
            err_msg = f"Video file not found or is invalid: {video_path}"
            logger.error(err_msg)
            raise FileNotFoundError(err_msg)
            
        base_path, _ = os.path.splitext(video_path)
        audio_path = f"{base_path}.wav"
        
        try:
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as e:
            logger.exception("Failed to retrieve ffmpeg executable path via imageio_ffmpeg.")
            raise e
        
        # Extract audio as 16kHz mono WAV (ideal for Whisper)
        command = [
            ffmpeg_exe,
            "-i", video_path,
            "-vn",          # Disable video stream
            "-acodec", "pcm_s16le",
            "-ar", "16000", # 16kHz sample rate
            "-ac", "1",     # Mono channel
            "-y",           # Overwrite output without prompting
            audio_path
        ]
        
        try:
            logger.info("Executing FFmpeg command to extract audio from: %s", video_path)
            # Capture stdout and stderr to provide detailed diagnostics on failure
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info("Successfully extracted audio to: %s", audio_path)
            return audio_path
        except subprocess.CalledProcessError as e:
            logger.error("FFmpeg execution failed with exit code %d.", e.returncode)
            if e.stderr:
                logger.error("FFmpeg error trace:\n%s", e.stderr)
            raise e

