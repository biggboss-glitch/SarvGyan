"""
Document Processor Module

Handles extraction of text content from PDF and DOCX files.
Supports chunking for optimal embedding and retrieval.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional

from PyPDF2 import PdfReader
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text content from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text as a single string.
    """
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract all text content from a DOCX file.

    Args:
        file_path: Path to the DOCX file.

    Returns:
        Extracted text as a single string.
    """
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text.strip()


def extract_text(file_path: str, file_type: str) -> str:
    """Extract text from a document based on its type.

    Args:
        file_path: Path to the document.
        file_type: Type of file ("pdf" or "docx").

    Returns:
        Extracted text content.

    Raises:
        ValueError: If file_type is not supported.
    """
    file_type = file_type.lower()
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type in ("docx", "doc"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}. Supported: pdf, docx")


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[str]:
    """Split text into overlapping chunks for embedding.

    Args:
        text: The full text to split.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of overlapping characters between chunks.

    Returns:
        List of text chunks.
    """
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - chunk_overlap

    return [c for c in chunks if c]


def process_document(
    file_path: str,
    file_type: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> Dict:
    """Process a document: extract text and split into chunks.

    Args:
        file_path: Path to the document.
        file_type: Type of file ("pdf" or "docx").
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between chunks.

    Returns:
        Dictionary with 'text', 'chunks', 'metadata'.
    """
    text = extract_text(file_path, file_type)
    chunks = chunk_text(text, chunk_size, chunk_overlap)

    return {
        "text": text,
        "chunks": chunks,
        "metadata": {
            "source": os.path.basename(file_path),
            "file_type": file_type,
            "total_chunks": len(chunks),
            "total_characters": len(text),
        },
    }
