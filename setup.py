"""
Setup script to download and configure ffmpeg for the project
"""

import urllib.request
import zipfile
import os
import ssl
from pathlib import Path

# Disable SSL verification for download (needed for some systems)
ssl._create_default_https_context = ssl._create_unverified_context

FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
FFMPEG_DIR = "ffmpeg"
FFMPEG_ZIP = "ffmpeg.zip"


def download_ffmpeg():
    """Download ffmpeg from GitHub releases"""
    print("Downloading ffmpeg...")
    print(f"URL: {FFMPEG_URL}")
    print("This may take a few minutes (~100MB)...\n")
    
    try:
        urllib.request.urlretrieve(FFMPEG_URL, FFMPEG_ZIP)
        print("[OK] Download complete!\n")
        return True
    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        return False


def extract_ffmpeg():
    """Extract ffmpeg zip file"""
    print("Extracting ffmpeg...")
    
    try:
        with zipfile.ZipFile(FFMPEG_ZIP, 'r') as zip_ref:
            zip_ref.extractall(FFMPEG_DIR)
        print("[OK] Extraction complete!\n")
        return True
    except Exception as e:
        print(f"[ERROR] Extraction failed: {e}")
        return False


def cleanup():
    """Remove the downloaded zip file"""
    try:
        if os.path.exists(FFMPEG_ZIP):
            os.remove(FFMPEG_ZIP)
            print("[OK] Cleaned up temporary files\n")
    except Exception as e:
        print(f"Warning: Could not remove {FFMPEG_ZIP}: {e}")


def verify_installation():
    """Verify ffmpeg was installed correctly"""
    ffmpeg_bin = Path(FFMPEG_DIR) / "ffmpeg-master-latest-win64-gpl" / "bin" / "ffmpeg.exe"
    
    if ffmpeg_bin.exists():
        print("[OK] ffmpeg installed successfully!")
        print(f"Location: {ffmpeg_bin.absolute()}\n")
        return True
    else:
        print("[ERROR] ffmpeg installation verification failed")
        return False


def main():
    print("="*70)
    print("FFMPEG SETUP FOR AUDIO TRANSCRIPTION")
    print("="*70)
    print()
    
    # Check if already installed
    ffmpeg_bin = Path(FFMPEG_DIR) / "ffmpeg-master-latest-win64-gpl" / "bin" / "ffmpeg.exe"
    if ffmpeg_bin.exists():
        print("[WARNING] ffmpeg is already installed!")
        response = input("Do you want to reinstall? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
        print()
    
    # Create ffmpeg directory
    Path(FFMPEG_DIR).mkdir(exist_ok=True)
    
    # Download
    if not download_ffmpeg():
        return
    
    # Extract
    if not extract_ffmpeg():
        cleanup()
        return
    
    # Cleanup
    cleanup()
    
    # Verify
    if verify_installation():
        print("="*70)
        print("SETUP COMPLETE!")
        print("="*70)
        print("You can now run: python transcribe.py")
        print("="*70)
    else:
        print("\nSetup may have failed. Please check the ffmpeg directory.")


if __name__ == "__main__":
    main()

