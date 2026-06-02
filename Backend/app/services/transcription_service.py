from faster_whisper import WhisperModel
import time

class TranscriptionService:
    def __init__(self):
        # We initialize the model here. It downloads the base model on first run.
        # compute_type="int8" is used for memory efficiency.
        self.model = WhisperModel("base", device="cpu", compute_type="int8")

    def transcribe_video(self, audio_path: str) -> dict:
        """
        Transcribes the audio file using faster-whisper.
        Returns the transcript text and source.
        """
        start_time = time.time()
        print(f"[WHISPER] Starting transcription for {audio_path}...")
        
        segments, info = self.model.transcribe(audio_path, beam_size=5)
        
        transcript_text = ""
        for segment in segments:
            transcript_text += segment.text + " "
            
        duration = time.time() - start_time
        print(f"[WHISPER] Transcription complete")
        print(f"[WHISPER] Duration: {duration:.2f} seconds")
        
        return {
            "transcript": transcript_text.strip(),
            "source": "whisper"
        }
