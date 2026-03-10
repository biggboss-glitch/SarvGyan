"""
Utilities Module

Helper functions for file handling, audio processing, and general utilities.
"""

import os
import tempfile
import hashlib
from pathlib import Path
from typing import Optional


# Project directories
DATA_DIR = Path("data")
UPLOADS_DIR = DATA_DIR / "uploads"
TEMP_DIR = DATA_DIR / "temp"


def ensure_directories() -> None:
    """Create all required data directories if they don't exist."""
    for directory in [UPLOADS_DIR, TEMP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(uploaded_file, filename: Optional[str] = None) -> str:
    """Save a Streamlit uploaded file to the uploads directory.

    Args:
        uploaded_file: Streamlit UploadedFile object.
        filename: Optional custom filename. Defaults to the original name.

    Returns:
        Path to the saved file.
    """
    ensure_directories()
    filename = filename or uploaded_file.name
    file_path = UPLOADS_DIR / filename

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(file_path)


def get_file_type(filename: str) -> str:
    """Determine file type from filename extension.

    Args:
        filename: Name of the file.

    Returns:
        File type string ("pdf" or "docx").

    Raises:
        ValueError: If the file type is not supported.
    """
    ext = Path(filename).suffix.lower()
    type_map = {
        ".pdf": "pdf",
        ".docx": "docx",
        ".doc": "docx",
    }
    if ext not in type_map:
        raise ValueError(f"Unsupported file type: {ext}")
    return type_map[ext]


def generate_doc_id(filename: str) -> str:
    """Generate a unique document ID from a filename.

    Args:
        filename: Name of the file.

    Returns:
        A short hash-based document ID.
    """
    hash_val = hashlib.md5(filename.encode()).hexdigest()[:8]
    base_name = Path(filename).stem
    return f"{base_name}_{hash_val}"


def format_file_size(size_bytes: int) -> str:
    """Format a file size in bytes to a human-readable string.

    Args:
        size_bytes: File size in bytes.

    Returns:
        Human-readable size string (e.g., "1.5 MB").
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def text_to_speech(text: str, output_path: Optional[str] = None) -> str:
    """Convert text to speech using gTTS.

    Args:
        text: Text to convert.
        output_path: Optional path for the audio file.

    Returns:
        Path to the generated audio file.
    """
    from gtts import gTTS

    ensure_directories()
    if output_path is None:
        output_path = str(TEMP_DIR / "response_audio.mp3")

    tts = gTTS(text=text, lang="en")
    tts.save(output_path)

    return output_path


def cleanup_temp_files() -> None:
    """Remove all temporary files from the temp directory."""
    if TEMP_DIR.exists():
        for file in TEMP_DIR.iterdir():
            if file.is_file() and file.name != ".gitkeep":
                file.unlink()
