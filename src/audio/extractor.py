"""
Audio extraction utilities for the video translator application.
"""
import os
import subprocess
from pathlib import Path

from src.utils.logger import get_logger
from config import OUTPUT_DIR, FFMPEG_AUDIO_PARAMS

logger = get_logger(__name__)

def extract_audio(video_path):
    """
    Extract audio from video file using ffmpeg.
    
    Args:
        video_path (str): Path to the input video file
        
    Returns:
        Path: Path to the extracted audio file
        
    Raises:
        Exception: If audio extraction fails
    """
    try:
        video_path = Path(video_path)
        logger.info(f"Extracting audio from video: {video_path}")
        
        # Create output filename based on input filename
        video_name = video_path.stem
        audio_path = OUTPUT_DIR / f"{video_name}_audio.{FFMPEG_AUDIO_PARAMS['format']}"
        
        # Use ffmpeg to extract audio
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # No video
            '-acodec', FFMPEG_AUDIO_PARAMS['codec'],
            '-ar', str(FFMPEG_AUDIO_PARAMS['sample_rate']),
            '-ac', str(FFMPEG_AUDIO_PARAMS['channels']),
            '-y',  # Overwrite output file
            str(audio_path)
        ]
        
        logger.debug(f"Running command: {' '.join(cmd)}")
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            error_message = f"Audio extraction failed: {process.stderr}"
            logger.error(error_message)
            raise Exception(error_message)
        
        logger.info(f"Audio extraction successful: {audio_path}")
        return audio_path
    except Exception as e:
        logger.error(f"Audio extraction failed: {str(e)}", exc_info=True)
        raise Exception(f"Audio extraction failed: {str(e)}")

def get_video_duration(video_path):
    """
    Get the duration of a video file in seconds.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        float: Duration in seconds
        
    Raises:
        Exception: If duration extraction fails
    """
    try:
        video_path = Path(video_path)
        logger.info(f"Getting duration for video: {video_path}")
        
        cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            str(video_path)
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0 or not process.stdout.strip():
            error_message = f"Failed to get video duration: {process.stderr}"
            logger.error(error_message)
            raise Exception(error_message)
        
        duration = float(process.stdout.strip())
        logger.info(f"Video duration: {duration} seconds")
        return duration
    except Exception as e:
        logger.error(f"Failed to get video duration: {str(e)}", exc_info=True)
        raise Exception(f"Failed to get video duration: {str(e)}")

def create_silent_audio(duration, output_path=None):
    """
    Create a silent audio file with the specified duration.
    
    Args:
        duration (float): Duration in seconds
        output_path (str, optional): Path to save the silent audio file
        
    Returns:
        Path: Path to the silent audio file
        
    Raises:
        Exception: If silent audio creation fails
    """
    try:
        if output_path is None:
            output_path = OUTPUT_DIR / f"silent_{int(duration)}s.wav"
        else:
            output_path = Path(output_path)
            
        logger.info(f"Creating silent audio track of {duration} seconds")
        
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', f'anullsrc=r={FFMPEG_AUDIO_PARAMS["sample_rate"]}:cl=stereo',
            '-t', str(duration),
            '-q:a', '0',
            '-y',
            str(output_path)
        ]
        
        logger.debug(f"Running command: {' '.join(cmd)}")
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            error_message = f"Silent audio creation failed: {process.stderr}"
            logger.error(error_message)
            raise Exception(error_message)
        
        logger.info(f"Silent audio created: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to create silent audio: {str(e)}", exc_info=True)
        raise Exception(f"Failed to create silent audio: {str(e)}")
