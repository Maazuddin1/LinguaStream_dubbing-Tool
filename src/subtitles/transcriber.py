"""
Speech-to-text transcription for subtitle generation.
"""
import os
from pathlib import Path
import assemblyai as aai

from src.utils.logger import get_logger
from config import ASSEMBLYAI_API_KEY, OUTPUT_DIR

logger = get_logger(__name__)

# Configure AssemblyAI
aai.settings.api_key = ASSEMBLYAI_API_KEY

def generate_subtitles(audio_path, language_code="en"):
    """
    Generate subtitles using AssemblyAI's speech recognition.
    
    Args:
        audio_path (str): Path to the audio file
        language_code (str): Language code for transcription
        
    Returns:
        Path: Path to the generated SRT subtitle file
        
    Raises:
        Exception: If subtitle generation fails
    """
    try:
        audio_path = Path(audio_path)
        logger.info(f"Transcribing audio with AssemblyAI: {audio_path}")
        
        # Create output filename
        audio_name = audio_path.stem
        srt_path = OUTPUT_DIR / f"{audio_name}_subtitles.srt"
        
        # Configure transcription options
        config = aai.TranscriptionConfig(
            language_code=language_code,
            punctuate=True,
            format_text=True
        )
        
        # Transcribe audio
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(str(audio_path), config=config)
        
        if not transcript or not hasattr(transcript, 'export_subtitles_srt'):
            error_message = "Transcription failed or returned invalid result"
            logger.error(error_message)
            raise Exception(error_message)
        
        # Export as SRT
        logger.info(f"Saving subtitles to: {srt_path}")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(transcript.export_subtitles_srt())
            
        logger.info(f"Subtitle generation successful: {srt_path}")
        return srt_path
    except Exception as e:
        logger.error(f"Subtitle generation failed: {str(e)}", exc_info=True)
        raise Exception(f"Subtitle generation failed: {str(e)}")
