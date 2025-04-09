# Video Translator 🌐

A complete video translation system that converts videos into multiple languages by translating both subtitles and audio.

## Features

- 🎬 Video to text transcription using AssemblyAI
- 🔤 Translation of transcripts to multiple languages
- 🔊 Text-to-speech generation in target languages
- 📝 Subtitle generation and embedding
- 🎞️ Final video with translated audio and subtitles

## Supported Languages

- English
- Spanish
- French
- German
- Japanese
- Hindi
- And more...

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/video-translator.git
cd video-translator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
   - On Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - On macOS (with Homebrew): `brew install ffmpeg`
   - On Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)

4. Set up your API key:
   - Copy `.env.example` to `.env`
   - Add your AssemblyAI API key to the `.env` file

## Usage

1. Run the app:
```bash
python app.py
```

2. Open the provided URL in your browser
3. Upload a video file
4. Select source and target languages
5. Click "Translate" and wait for processing

## Deployment on Hugging Face Spaces

This project is configured for easy deployment to [Hugging Face Spaces](https://huggingface.co/spaces). To deploy:

1. Fork this repository
2. Create a new Space on Hugging Face
3. Connect your GitHub repository
4. Set the required environment variables (ASSEMBLYAI_API_KEY)
5. Deploy!

## Project Structure

```
video-translator/
├── app.py                    # Main Gradio app entry point
├── config.py                 # Configuration and constants
├── src/                      # Source code
│   ├── audio/                # Audio processing
│   ├── video/                # Video processing
│   ├── subtitles/            # Subtitle handling
│   └── utils/                # Utilities and helpers
└── outputs/                  # Output directory
```

## Environment Variables

- `ASSEMBLYAI_API_KEY`: API key for AssemblyAI (required)
- `DEBUG`: Set to "True" for debug logging (optional)
- `OUTPUT_DIR`: Custom output directory path (optional)

## License

MIT License
