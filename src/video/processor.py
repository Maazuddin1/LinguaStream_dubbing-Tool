"""
Video processing utilities for combining video, audio, and subtitles.
"""
import os
import shutil
import subprocess
from pathlib import Path
import tempfile

from src.utils.logger import get_logger
from config import OUTPUT_DIR, SUBTITLE_FONT_SIZE

logger = get_logger(__name__)

def combine_video_audio_subtitles(video_path, audio_path, srt_path, output_path=None):
    """
    Combine video with translated audio and subtitles.
    
    Args:
        video_path (str): Path to the video file
        audio_path (str): Path to the translated audio file
        srt_path (str): Path to the subtitle file
        output_path (str, optional): Path for the output video
        
    Returns:
        Path: Path to the output video
        
    Raises:
        Exception: If combining fails
    """
    try:
        video_path = Path(video_path)
        audio_path = Path(audio_path)
        srt_path = Path(srt_path)
        
        # Generate output path if not provided
        if output_path is None:
            lang_code = srt_path.stem.split('_')[-1]
            output_path = OUTPUT_DIR / f"{video_path.stem}_translated_{lang_code}.mp4"
        else:
            output_path = Path(output_path)
            
        logger.info(f"Combining video, audio, and subtitles")
        
        # Verify that all input files exist
        if not video_path.exists():
            raise FileNotFoundError(f"Video file does not exist: {video_path}")
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file does not exist: {audio_path}")
        if not srt_path.exists():
            raise FileNotFoundError(f"Subtitle file does not exist: {srt_path}")
            
        logger.info(f"Input files verified: Video: {video_path.stat().st_size} bytes, "
                   f"Audio: {audio_path.stat().st_size} bytes, "
                   f"Subtitles: {srt_path.stat().st_size} bytes")
        
        # Try different methods to combine
        methods = [
            combine_method_subtitles_filter,
            combine_method_with_temp,
            combine_method_no_subtitles
        ]
        
        success = False
        error_messages = []
        
        for i, method in enumerate(methods):
            try:
                logger.info(f"Trying combination method {i+1}/{len(methods)}")
                result = method(video_path, audio_path, srt_path, output_path)
                if result and Path(result).exists() and Path(result).stat().st_size > 0:
                    success = True
                    output_path = result
                    logger.info(f"Combination method {i+1} succeeded")
                    break
                else:
                    error_messages.append(f"Method {i+1} failed: Result file not valid")
            except Exception as e:
                error_message = f"Method {i+1} failed: {str(e)}"
                logger.warning(error_message)
                error_messages.append(error_message)
        
        if not success:
            error_message = f"All combination methods failed: {'; '.join(error_messages)}"
            logger.error(error_message)
            raise Exception(error_message)
            
        logger.info(f"Successfully combined video, audio, and subtitles: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Combining failed: {str(e)}", exc_info=True)
        raise Exception(f"Combining failed: {str(e)}")

def combine_method_subtitles_filter(video_path, audio_path, srt_path, output_path):
    """
    Combine video, audio, and subtitles using ffmpeg with subtitle filter.
    
    Args:
        video_path (Path): Path to the video file
        audio_path (Path): Path to the translated audio file
        srt_path (Path): Path to the subtitle file
        output_path (Path): Path for the output video
        
    Returns:
        Path: Path to the output video
    """
    logger.info(f"Using subtitles filter method")
    
    # Use ffmpeg to combine video, audio, and subtitles
    cmd = [
        'ffmpeg',
        '-i', str(video_path),  # Video input
        '-i', str(audio_path),  # Audio input
        '-vf', f"subtitles={str(srt_path)}:force_style='FontSize={SUBTITLE_FONT_SIZE}'",  # Subtitle filter
        '-map', '0:v',  # Map video from first input
        '-map', '1:a',  # Map audio from second input
        '-c:v', 'libx264',  # Video codec
        '-c:a', 'aac',  # Audio codec
        '-strict', 'experimental',
        '-b:a', '192k',  # Audio bitrate
        '-y',  # Overwrite output
        str(output_path)
    ]
    
    logger.debug(f"Running command: {' '.join(cmd)}")
    process = subprocess.run(cmd, capture_output=True, text=True)
    
    if process.returncode != 0:
        error_message = f"FFmpeg subtitles filter method failed: {process.stderr}"
        logger.error(error_message)
        raise Exception(error_message)
    
    return output_path

def combine_method_with_temp(video_path, audio_path, srt_path, output_path):
    """
    Combine video, audio, and subtitles using temporary files.
    
    Args:
        video_path (Path): Path to the video file
        audio_path (Path): Path to the translated audio file
        srt_path (Path): Path to the subtitle file
        output_path (Path): Path for the output video
        
    Returns:
        Path: Path to the output video
    """
    logger.info(f"Using temporary file method")
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="video_combine_", dir=OUTPUT_DIR / "temp"))
    try:
        # Step 1: Combine video with audio
        temp_video_audio = temp_dir / "video_with_audio.mp4"
        cmd1 = [
            'ffmpeg',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-map', '0:v',
            '-map', '1:a',
            '-y',
            str(temp_video_audio)
        ]
        
        logger.debug(f"Running command (step 1): {' '.join(cmd1)}")
        process1 = subprocess.run(cmd1, capture_output=True, text=True)
        
        if process1.returncode != 0:
            error_message = f"Step 1 failed: {process1.stderr}"
            logger.error(error_message)
            raise Exception(error_message)
            
        # Step 2: Add subtitles to the combined video
        cmd2 = [
            'ffmpeg',
            '-i', str(temp_video_audio),
            '-vf', f"subtitles={str(srt_path)}:force_style='FontSize={SUBTITLE_FONT_SIZE}'",
            '-c:a', 'copy',
            '-y',
            str(output_path)
        ]
        
        logger.debug(f"Running command (step 2): {' '.join(cmd2)}")
        process2 = subprocess.run(cmd2, capture_output=True, text=True)
        
        if process2.returncode != 0:
            error_message = f"Step 2 failed: {process2.stderr}"
            logger.error(error_message)
            raise Exception(error_message)
            
        return output_path
    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(temp_dir)
            logger.debug(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp directory: {str(e)}")

def combine_method_no_subtitles(video_path, audio_path, srt_path, output_path):
    """
    Fallback method: Combine only video and audio without subtitles.
    
    Args:
        video_path (Path): Path to the video file
        audio_path (Path): Path to the translated audio file
        srt_path (Path): Path to the subtitle file (unused in this method)
        output_path (Path): Path for the output video
        
    Returns:
        Path: Path to the output video
    """
    logger.info(f"Using fallback method (no subtitles)")
    
    # Just combine video and audio as fallback
    cmd = [
        'ffmpeg',
        '-i', str(video_path),
        '-i', str(audio_path),
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-map', '0:v',
        '-map', '1:a',
        '-y',
        str(output_path)
    ]
    
    logger.debug(f"Running command: {' '.join(cmd)}")
    process = subprocess.run(cmd, capture_output=True, text=True)
    
    if process.returncode != 0:
        error_message = f"Fallback method failed: {process.stderr}"
        logger.error(error_message)
        raise Exception(error_message)
    
    logger.warning("Video was combined without subtitles")
    return output_path
