import logging
import time
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class TranscriptionService:
    def __init__(self):
        """
        Initializes the faster-whisper model.
        Detects if CUDA is available for GPU acceleration and falls back to CPU if not.
        """
        device = "cpu"
        compute_type = "int8"
        
        try:
            import torch
            if torch.cuda.is_available():
                device = "cuda"
                compute_type = "float16"
                logger.info("CUDA GPU detected. Configuring WhisperModel on 'cuda' with float16.")
            else:
                logger.info("CUDA GPU not detected. Configuring WhisperModel on 'cpu' with int8.")
        except ImportError:
            logger.info("PyTorch not installed or unable to import. Configuring WhisperModel on 'cpu' with int8.")
        except Exception as e:
            logger.warning("Error checking CUDA availability: %s. Defaulting to 'cpu' with int8.", e)

        try:
            # We initialize the model here. It downloads the base model on first run.
            self.model = WhisperModel("base", device=device, compute_type=compute_type)
        except Exception as e:
            logger.exception("Failed to initialize WhisperModel on device %s. Falling back to CPU with int8.", device)
            # Fallback configuration
            self.model = WhisperModel("base", device="cpu", compute_type="int8")

    def transcribe_video(self, audio_path: str) -> dict:
        """
        Transcribes the audio file using faster-whisper.
        
        Args:
            audio_path: Path to the local audio file to transcribe.
            
        Returns:
            A dictionary containing the transcript text and the transcription source.
        """
        start_time = time.time()
        logger.info("Starting Whisper transcription for audio file: %s", audio_path)
        
        try:
            segments, info = self.model.transcribe(audio_path, beam_size=5)
            
            transcript_text = ""
            for segment in segments:
                transcript_text += segment.text + " "
                
            duration = time.time() - start_time
            logger.info("Whisper transcription completed in %.2f seconds", duration)
            
            return {
                "transcript": transcript_text.strip(),
                "source": "whisper"
            }
        except Exception as e:
            logger.exception("Error occurred during Whisper transcription for path: %s", audio_path)
            # Return an empty transcript instead of crashing, so the ingest pipeline can continue with metadata only
            return {
                "transcript": "",
                "source": "whisper_error"
            }

