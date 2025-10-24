# Audio Transcription Tool

Automated audio transcription using OpenAI Whisper for Arabic language.

## Project Structure

```
.
├── audio/              # Place your audio files here
├── transcriptions/     # Transcription results saved here
├── transcribe.py       # Main transcription script
└── requirements.txt    # Python dependencies
```

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Setup ffmpeg (required for audio processing):
```bash
python setup.py
```

3. Place your audio files in the `audio/` folder

## Usage

Run the transcription tool:
```bash
python transcribe.py
```

The script will:
- Process all `.mp3` and `.mp4` files from `audio/` folder
- Transcribe audio using Whisper (Arabic language)
- Save each transcription to `transcriptions/` with the same filename (`.txt` extension)

## Configuration

Edit `transcribe.py` to customize:

```python
AUDIO_FORMATS = ['.mp3', '.mp4']  # Supported formats
WHISPER_MODEL = "small"            # Model size: tiny, base, small, medium, large
LANGUAGE = "ar"                    # Language code (ar = Arabic)
MAX_WORKERS = None                 # None = auto (uses all CPU cores), or set number (e.g., 4)
```

## Performance

- **Parallel Processing**: Uses all available CPU cores by default
- **Speed**: Processes multiple files simultaneously (4-8x faster than sequential)
- **800 files**: ~40-60 minutes (vs ~5 hours sequential)
- Adjust `MAX_WORKERS` to control CPU usage

## Output Format

Each transcription file includes:
- Audio filename
- Detected language
- Full transcription text
- Timestamped segments (with start/end times)

## Notes

- First run will download the Whisper model (~500MB for 'small')
- Larger models (medium, large) are more accurate but slower
- Works offline after initial model download

