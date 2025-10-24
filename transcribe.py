"""
Audio Transcription Tool using OpenAI Whisper
Processes all audio files from audio/ folder and saves transcriptions to transcriptions/ folder
"""

import whisper
import os
import time
from datetime import timedelta
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

# Add ffmpeg to PATH if it exists in the project
FFMPEG_BIN = Path("ffmpeg") / "ffmpeg-master-latest-win64-gpl" / "bin"
if FFMPEG_BIN.exists():
    os.environ["PATH"] = str(FFMPEG_BIN.absolute()) + os.pathsep + os.environ["PATH"]

# Configuration
AUDIO_FORMATS = ['.mp3', '.mp4']  # Configurable audio formats
AUDIO_DIR = "audio"
TRANSCRIPTIONS_DIR = "transcriptions"
WHISPER_MODEL = "small"  # Options: tiny, base, small, medium, large
LANGUAGE = "ar"  # Arabic
MAX_WORKERS = 2  # None = auto-detect CPU cores, or set a number (e.g., 4)


def ensure_directories():
    """Create necessary directories if they don't exist"""
    Path(AUDIO_DIR).mkdir(exist_ok=True)
    Path(TRANSCRIPTIONS_DIR).mkdir(exist_ok=True)


def get_audio_files():
    """Get all audio files from the audio directory"""
    audio_files = []
    for format in AUDIO_FORMATS:
        audio_files.extend(Path(AUDIO_DIR).glob(f"*{format}"))
    return sorted(audio_files)


def is_already_transcribed(audio_path):
    """Check if transcription file already exists for this audio file"""
    output_filename = audio_path.stem + ".txt"
    output_path = Path(TRANSCRIPTIONS_DIR) / output_filename
    return output_path.exists()


def process_single_file(audio_path_str):
    """
    Worker function to process a single audio file.
    This runs in a separate process for parallel execution.
    """
    audio_path = Path(audio_path_str)
    
    try:
        # Each process loads its own model
        model = whisper.load_model(WHISPER_MODEL)
        
        # Transcribe
        result = model.transcribe(
            str(audio_path),
            language=LANGUAGE,
            task="transcribe",
            fp16=False  # CPU compatibility
        )
        
        # Save transcription
        output_filename = audio_path.stem + ".txt"
        output_path = Path(TRANSCRIPTIONS_DIR) / output_filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Audio File: {audio_path.name}\n")
            f.write(f"Detected Language: {result['language']}\n")
            f.write(f"{'='*70}\n\n")
            f.write(f"Transcription:\n")
            f.write(result['text'])
            f.write("\n\n")
            
            # Add detailed segments with timestamps if available
            if 'segments' in result and len(result['segments']) > 0:
                f.write(f"\n{'='*70}\n")
                f.write("Detailed Segments with Timestamps:\n")
                f.write(f"{'='*70}\n")
                for segment in result['segments']:
                    start_time = segment['start']
                    end_time = segment['end']
                    text = segment['text']
                    f.write(f"[{start_time:.2f}s - {end_time:.2f}s]: {text}\n")
        
        return {
            'filename': audio_path.name,
            'success': True,
            'error': None
        }
        
    except Exception as e:
        return {
            'filename': audio_path.name,
            'success': False,
            'error': str(e)
        }


def main():
    """Main function to process all audio files"""
    # Start timer
    start_time = time.time()
    
    # Determine number of workers
    num_workers = MAX_WORKERS if MAX_WORKERS else multiprocessing.cpu_count()
    
    print("\n" + "="*70)
    print("WHISPER AUDIO TRANSCRIPTION TOOL (PARALLEL MODE)")
    print("="*70)
    print(f"Audio formats: {', '.join(AUDIO_FORMATS)}")
    print(f"Language: Arabic ({LANGUAGE})")
    print(f"Model: {WHISPER_MODEL}")
    print(f"Parallel workers: {num_workers} (CPU cores: {multiprocessing.cpu_count()})")
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Ensure directories exist
    ensure_directories()
    
    # Get all audio files
    audio_files = get_audio_files()
    
    if not audio_files:
        print(f"\n[WARNING] No audio files found in '{AUDIO_DIR}/' folder")
        print(f"Please add {' or '.join(AUDIO_FORMATS)} files to the '{AUDIO_DIR}/' directory")
        return
    
    # Filter out already transcribed files
    already_done = [f for f in audio_files if is_already_transcribed(f)]
    files_to_process = [f for f in audio_files if not is_already_transcribed(f)]
    
    print(f"\nFound {len(audio_files)} audio file(s) total")
    if already_done:
        print(f"[SKIP] {len(already_done)} already transcribed (skipping)")
        print(f"[TODO] {len(files_to_process)} remaining to process")
    else:
        print(f"[TODO] {len(files_to_process)} to process")
    
    if not files_to_process:
        print(f"\n[OK] All files already transcribed! Nothing to do.")
        return
    
    print(f"\nProcessing {num_workers} files simultaneously...\n")
    
    # Process files in parallel
    successful = 0
    failed = 0
    completed = 0
    
    # Convert Path objects to strings for multiprocessing
    audio_paths = [str(f) for f in files_to_process]
    
    print("="*70)
    print("PROCESSING...")
    print("="*70)
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Submit all tasks
        future_to_file = {executor.submit(process_single_file, path): path for path in audio_paths}
        
        # Process results as they complete
        for future in as_completed(future_to_file):
            completed += 1
            result = future.result()
            
            if result['success']:
                successful += 1
                print(f"[{completed}/{len(files_to_process)}] [OK] {result['filename']}")
            else:
                failed += 1
                print(f"[{completed}/{len(files_to_process)}] [ERROR] {result['filename']}: {result['error']}")
    
    # Summary with total execution time
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n{'='*70}")
    print("PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"Total files found: {len(audio_files)}")
    if already_done:
        print(f"[SKIP] Already done: {len(already_done)}")
    print(f"[PROCESSED] Attempted: {len(files_to_process)}")
    print(f"[OK] Successfully transcribed: {successful}")
    if failed > 0:
        print(f"[ERROR] Failed: {failed}")
    print(f"\nTranscriptions saved in: {TRANSCRIPTIONS_DIR}/")
    print(f"\nEnd time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total execution time: {str(timedelta(seconds=int(elapsed_time)))}")
    if len(files_to_process) > 0:
        print(f"Average time per file: {elapsed_time/len(files_to_process):.2f}s")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()

