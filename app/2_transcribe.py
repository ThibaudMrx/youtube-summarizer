import logging
import whisper
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def transcribe_audio(audio_path, model_name="base"):
    logger.info(f"Loading Whisper model: {model_name}")
    model = whisper.load_model(model_name, download_root=None, in_memory=True)
    model_size = sum(p.numel() for p in model.parameters() if p.requires_grad) * 4 / (1024 ** 2)  # size in MB
    logger.info(f"Model loaded into memory. Size: {model_size:.2f} MB")
    
    logger.info(f"Transcribing audio file: {audio_path}")
    result = model.transcribe(audio_path)
    
    logger.info("Transcription completed successfully")
    return result["text"]

audio_path = "audio.mp3"

if os.path.exists(audio_path):
    logger.info(f"Audio file found: {audio_path}")
    transcription = transcribe_audio(audio_path)
    with open("transcription.txt", "w") as f:
        f.write(transcription)
    logger.info("Transcription saved to transcription.txt")
    logger.info(f"Transcription: {transcription}")
else:
    logger.error(f"Audio file not found: {audio_path}")

