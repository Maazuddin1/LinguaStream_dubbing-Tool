"""
Text-to-speech audio generation for translated subtitles.
"""
import os
import time
import shutil
import tempfile
from pathlib import Path
from tqdm import tqdm
import subprocess

from gtts import gTTS
import pysrt

from src.utils.logger import get_logger
from src.audio.extractor import create_silent_audio
from config import OUTPUT_DIR, TTS_VOICES, MAX_RETRY_ATTEMPTS

logger = get_logger(__name__)

def generate_translated_audio(srt_path, target_lang, video_duration=180):
    """
    Generate translated audio using text-to-speech for each subtitle.
    
    Args:
        srt_path (str): Path to the SRT subtitle file
        target_lang (str): Target language code (e.g., 'en', 'es')
        video_duration (float): Duration of the original video in seconds
        
    Returns:
        Path: Path to the translated audio file
        
    Raises:
        Exception: If audio generation fails
    """
    try:
        srt_path = Path(srt_path)
        logger.info(f"Generating translated audio for {target_lang} from {srt_path}")
        
        # Load subtitles
        subs = pysrt.open(srt_path, encoding="utf-8")
        logger.info(f"Loaded {len(subs)} subtitles from SRT file")
        
        # Create temporary directory for audio chunks
        temp_dir = Path(tempfile.mkdtemp(prefix=f"audio_{target_lang}_", dir=OUTPUT_DIR / "temp"))
        logger.debug(f"Created temporary directory: {temp_dir}")
        
        # Generate TTS for each subtitle
        audio_files = []
        timings = []
        
        logger.info(f"Generating speech for {len(subs)} subtitles in {target_lang}")
        for i, sub in enumerate(tqdm(subs, desc=f"Generating {target_lang} speech")):
            text = sub.text.strip()
            if not text:
                continue
                
            # Get timing information
            start_time = (sub.start.hours * 3600 + 
                         sub.start.minutes * 60 + 
                         sub.start.seconds + 
                         sub.start.milliseconds / 1000)
            
            end_time = (sub.end.hours * 3600 + 
                       sub.end.minutes * 60 + 
                       sub.end.seconds + 
                       sub.end.milliseconds / 1000)
            
            duration = end_time - start_time
            
            # Generate TTS audio
            tts_lang = TTS_VOICES.get(target_lang, target_lang)
            audio_file = temp_dir / f"chunk_{i:04d}.mp3"
            
            # Add a retry mechanism
            retry_count = 0
            while retry_count < MAX_RETRY_ATTEMPTS:
                try:
                    # For certain languages, use slower speed which might improve reliability
                    slow_option = target_lang in ["hi", "ja", "zh-CN", "ar"] 
                    tts = gTTS(text=text, lang=target_lang, slow=slow_option)
                    tts.save(str(audio_file))
                    
                    if audio_file.exists() and audio_file.stat().st_size > 0:
                        break
                    else:
                        raise Exception("Generated audio file is empty")
                        
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"TTS attempt {retry_count} failed for {target_lang}: {str(e)}")
                    time.sleep(1)  # Wait before retrying
                    
                    # If still failing after retries, try with shorter text
                    if retry_count == MAX_RETRY_ATTEMPTS - 1 and len(text) > 100:
                        logger.warning(f"Trying with shortened text for {target_lang}")
                        shortened_text = text[:100] + "..."
                        tts = gTTS(text=shortened_text, lang=target_lang, slow=True)
                        tts.save(str(audio_file))
            
            if audio_file.exists() and audio_file.stat().st_size > 0:
                audio_files.append(audio_file)
                timings.append((start_time, end_time, duration, audio_file))
            else:
                logger.warning(f"Failed to generate audio for subtitle {i}")
        
        # Check if we generated any audio files
        if not audio_files:
            logger.warning(f"No audio files were generated for {target_lang}")
            # Create a silent audio file as fallback
            silent_audio = OUTPUT_DIR / f"translated_audio_{target_lang}.wav"
            create_silent_audio(video_duration, silent_audio)
            return silent_audio
        
        # Create a silent audio track as base
        silence_file = temp_dir / "silence.wav"
        create_silent_audio(video_duration, silence_file)
        
        # Create filter complex for audio mixing
        filter_complex = []
        input_count = 1  # Starting with 1 because 0 is the silence track
        
        # Start with silent track
        filter_parts = ["[0:a]"]
        
        # Add each audio segment
        for start_time, end_time, duration, audio_file in timings:
            delay_ms = int(start_time * 1000)
            filter_parts.append(f"[{input_count}:a]adelay={delay_ms}|{delay_ms}")
            input_count += 1
        
        # Mix all audio tracks
        filter_parts.append(f"amix=inputs={input_count}:dropout_transition=0:normalize=0[aout]")
        filter_complex = ";".join(filter_parts)
        
        # Build the ffmpeg command
        cmd = ['ffmpeg', '-y']
        
        # Add silent base track
        cmd.extend(['-i', str(silence_file)])
        
        # Add all audio chunks
        for audio_file in audio_files:
            cmd.extend(['-i', str(audio_file)])
        
        # Add filter complex and output
        output_audio = OUTPUT_DIR / f"translated_audio_{target_lang}.mp3"

        output_audio = OUTPUT_DIR / f"translated_audio_{target_lang}.wav"
        cmd.extend([
            '-filter_complex', filter_complex,
            '-map', '[aout]',
            output_audio
        ])
        
        # Run the command
        logger.info(f"Combining {len(audio_files)} audio segments")
        logger.debug(f"Running command: {' '.join(cmd)}")
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            logger.error(f"Audio combination failed: {process.stderr}")
            # Create a fallback silent audio
            silent_audio = OUTPUT_DIR / f"translated_audio_{target_lang}.wav"
            create_silent_audio(video_duration, silent_audio)
            output_audio = silent_audio
        
        # Clean up temporary files
        try:
            shutil.rmtree(temp_dir)
            logger.debug(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp directory: {str(e)}")
        
        logger.info(f"Successfully created translated audio: {output_audio}")
        return output_audio
    except Exception as e:
        logger.error(f"Audio translation failed: {str(e)}", exc_info=True)
        
        # Create an emergency fallback silent audio
        try:
            silent_audio = OUTPUT_DIR / f"translated_audio_{target_lang}.wav"
            create_silent_audio(video_duration, silent_audio)
            return silent_audio
        except:
            raise Exception(f"Audio translation failed: {str(e)}")
