"""
Main application entry point for the Video Translator.
"""
import os
import tempfile
import shutil
from pathlib import Path

import gradio as gr
from tqdm import tqdm

from src.utils.logger import get_logger
from src.audio.extractor import extract_audio, get_video_duration
from src.subtitles.transcriber import generate_subtitles
from src.subtitles.translator import translate_subtitles
from src.audio.generator import generate_translated_audio
from src.video.processor import combine_video_audio_subtitles
from config import LANGUAGES, OUTPUT_DIR, MAX_VIDEO_DURATION, MAX_UPLOAD_SIZE

logger = get_logger(__name__)

def process_video(video_file, source_lang, target_langs, progress=gr.Progress()):
    """
    Process video file and generate translated versions.
    
    Args:
        video_file (str): Path to the uploaded video file
        source_lang (str): Source language name
        target_langs (list): List of target language names
        progress (gr.Progress): Gradio progress tracker
        
    Returns:
        list: List of paths to translated videos
    """
    try:
        # Convert language names to codes
        source_lang_code = LANGUAGES[source_lang]
        target_lang_codes = [LANGUAGES[lang] for lang in target_langs]
        
        # Create temporary copy of uploaded file
        temp_dir = Path(tempfile.mkdtemp(prefix="video_processing_", dir=OUTPUT_DIR / "temp"))
        video_path = temp_dir / "input_video.mp4"
        shutil.copy2(video_file, video_path)
        
        logger.info(f"Processing video: {video_path}")
        logger.info(f"Source language: {source_lang} ({source_lang_code})")
        logger.info(f"Target languages: {', '.join(target_langs)} ({', '.join(target_lang_codes)})")
        
        # Check video duration
        progress(0.05, "Checking video duration...")
        duration = get_video_duration(video_path)
        if duration > MAX_VIDEO_DURATION:
            raise ValueError(f"Video is too long ({duration:.1f} seconds). Maximum allowed duration is {MAX_VIDEO_DURATION} seconds.")
        
        # Extract audio
        progress(0.1, "Extracting audio...")
        audio_path = extract_audio(video_path)
        
        # Generate subtitles
        progress(0.2, "Generating subtitles...")
        srt_path = generate_subtitles(audio_path, source_lang_code)
        
        # Translate subtitles
        progress(0.3, "Translating subtitles...")
        translated_srt_paths = translate_subtitles(srt_path, target_lang_codes)
        
        # Generate translated audio
        translated_audio_paths = {}
        for i, (lang_code, srt_path) in enumerate(translated_srt_paths.items()):
            progress_val = 0.3 + (0.4 * (i / len(translated_srt_paths)))
            progress(progress_val, f"Generating {[k for k, v in LANGUAGES.items() if v == lang_code][0]} audio...")
            audio_path = generate_translated_audio(srt_path, lang_code, duration)
            translated_audio_paths[lang_code] = audio_path
        
        # Combine video, audio, and subtitles
        output_videos = []
        for i, (lang_code, audio_path) in enumerate(translated_audio_paths.items()):
            progress_val = 0.7 + (0.25 * (i / len(translated_audio_paths)))
            lang_name = [k for k, v in LANGUAGES.items() if v == lang_code][0]
            progress(progress_val, f"Creating {lang_name} video...")
            
            srt_path = translated_srt_paths[lang_code]
            output_path = combine_video_audio_subtitles(video_path, audio_path, srt_path)
            output_videos.append(output_path)
        
        # Clean up
        try:
            shutil.rmtree(temp_dir)
        except:
            logger.warning(f"Failed to clean up temp directory: {temp_dir}")
            
        progress(1.0, "Translation complete!")
        return output_videos
        
    except Exception as e:
        logger.error(f"Video processing failed: {str(e)}", exc_info=True)
        raise gr.Error(f"Video processing failed: {str(e)}")

def create_app():
    """
    Create and configure the Gradio application.
    
    Returns:
        gr.Blocks: Configured Gradio application
    """
    with gr.Blocks(title="Video Translator") as app:
        gr.Markdown("# 🌐 Video Translator")
        gr.Markdown("Upload a video and translate it to different languages with subtitles!")
        
        with gr.Row():
            with gr.Column(scale=1):
                video_input = gr.Video(label="Upload Video")
                source_lang = gr.Dropdown(
                    choices=sorted(list(LANGUAGES.keys())), 
                    value="English", 
                    label="Source Language"
                )
                target_langs = gr.CheckboxGroup(
                    choices=[lang for lang in sorted(list(LANGUAGES.keys())) if lang != "English"],
                    value=["Spanish", "French"],
                    label="Target Languages"
                )
                translate_btn = gr.Button("Translate Video", variant="primary")
                
            with gr.Column(scale=2):
                output_gallery = gr.Gallery(
                    label="Translated Videos",
                    columns=2,
                    object_fit="contain",
                    height="auto"
                )
                
        translate_btn.click(
            fn=process_video,
            inputs=[video_input, source_lang, target_langs],
            outputs=output_gallery
        )
        
        gr.Markdown("""
        ## How it works
        
        1. Upload a video (max 10 minutes)
        2. Select the source language of your video
        3. Choose the target languages you want to translate to
        4. Click "Translate Video" and wait for processing
        5. Download your translated videos!
        
        ## Features
        
        - Automatic speech recognition using AssemblyAI
        - Translation to multiple languages
        - Generated speech in target languages
        - Embedded subtitles
        """)
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.launch(share=True, enable_queue=True)
    logger.info("Starting Video Translator application...")
