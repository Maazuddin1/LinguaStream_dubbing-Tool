"""
Configuration settings for the video translator application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# API Keys
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not ASSEMBLYAI_API_KEY:
    raise ValueError("ASSEMBLYAI_API_KEY is not set in environment variables or .env file")

# Output directory
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "outputs"))
OUTPUT_DIR.mkdir(exist_ok=True)

# Temp directory for processing
TEMP_DIR = OUTPUT_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# Debug mode
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Supported languages
LANGUAGES = {
    "English": "en",
    "Spanish": "es", 
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Hindi": "hi",
    "Chinese (Simplified)": "zh-CN",
    "Russian": "ru",
    "Italian": "it",
    "Portuguese": "pt",
    "Arabic": "ar",
    "Korean": "ko"
}

# TTS voice mapping for different languages
TTS_VOICES = {
    "en": "en-US",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
    "ja": "ja-JP",
    "hi": "hi-IN",
    "zh-CN": "zh-CN",
    "ru": "ru-RU",
    "it": "it-IT",
    "pt": "pt-BR",
    "ar": "ar",
    "ko": "ko"
}

# FFmpeg configurations
FFMPEG_AUDIO_PARAMS = {
    "format": "wav",
    "codec": "pcm_s16le",
    "sample_rate": 44100,
    "channels": 2
}

# Application settings
MAX_VIDEO_DURATION = 600  # in seconds (10 minutes)
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB
SUBTITLE_FONT_SIZE = 24
MAX_RETRY_ATTEMPTS = 3
