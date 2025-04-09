"""
Translation of subtitles into target languages.
"""
import os
from pathlib import Path
import time
from tqdm import tqdm
import pysrt
from deep_translator import GoogleTranslator

from src.utils.logger import get_logger
from config import OUTPUT_DIR, MAX_RETRY_ATTEMPTS

logger = get_logger(__name__)

def translate_subtitles(srt_path, target_langs):
    """
    Translate subtitles to target languages.
    
    Args:
        srt_path (str): Path to the SRT subtitle file
        target_langs (list): List of target language codes
        
    Returns:
        dict: Dictionary mapping language codes to translated SRT file paths
        
    Raises:
        Exception: If translation fails
    """
    try:
        srt_path = Path(srt_path)
        logger.info(f"Loading subtitles from: {srt_path}")
        
        # Load subtitles
        subs = pysrt.open(srt_path, encoding="utf-8")
        logger.info(f"Loaded {len(subs)} subtitles from SRT file")
        
        results = {}
        
        for lang_code in target_langs:
            logger.info(f"Translating to language code: {lang_code}")
            translated_subs = subs[:]  # Create a copy
            translator = GoogleTranslator(source="auto", target=lang_code)
            
            # Translate each subtitle with progress bar
            for i, sub in enumerate(tqdm(translated_subs, desc=f"Translating to {lang_code}")):
                retry_count = 0
                original_text = sub.text
                
                while retry_count < MAX_RETRY_ATTEMPTS:
                    try:
                        sub.text = translator.translate(original_text)
                        break
                    except Exception as e:
                        retry_count += 1
                        logger.warning(f"Translation attempt {retry_count} failed: {str(e)}")
                        time.sleep(1)  # Delay between retries
                        
                        # If final retry, preserve original text
                        if retry_count == MAX_RETRY_ATTEMPTS:
                            logger.warning(f"Failed to translate subtitle after {MAX_RETRY_ATTEMPTS} attempts")
                            sub.text = original_text
                
                # Log progress periodically
                if (i + 1) % 20 == 0 or i == len(translated_subs) - 1:
                    logger.info(f"Translated {i+1}/{len(translated_subs)} subtitles to {lang_code}")
            
            # Save translated subtitles
            output_path = OUTPUT_DIR / f"subtitles_{lang_code}.srt"
            logger.info(f"Saving translated subtitles to: {output_path}")
            translated_subs.save(str(output_path), encoding='utf-8')
            results[lang_code] = output_path
            
        logger.info(f"Successfully translated subtitles to {len(results)} languages")
        return results
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}", exc_info=True)
        raise Exception(f"Translation failed: {str(e)}")
