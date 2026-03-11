"""
Embeddings Module

Generates vector embeddings from text using sentence-transformers.
Uses the all-MiniLM-L6-v2 model by default for local, free embeddings.
"""

import os
import logging
from typing import List, Optional

from sentence_transformers import SentenceTransformer


# Default embedding model — lightweight and effective
DEFAULT_MODEL = "BAAI/bge-large-en-v1.5"

logger = logging.getLogger(__name__)

_model_cache: Optional[SentenceTransformer] = None


def get_embedding_model(model_name: Optional[str] = None) -> SentenceTransformer:
    """Get or initialize the embedding model (cached singleton).

    Args:
        model_name: Name of the sentence-transformers model to use.

    Returns:
        Initialized SentenceTransformer model.
    """
    global _model_cache

    model_name = model_name or os.getenv("EMBEDDING_MODEL", DEFAULT_MODEL)

    if _model_cache is None:
        logger.info(f"Loading embedding model into memory: {model_name}")
        _model_cache = SentenceTransformer(model_name)
        logger.info("Embedding model loaded successfully")

    return _model_cache


def generate_embeddings(texts: List[str], model_name: Optional[str] = None) -> List[List[float]]:
    """Generate embeddings for a list of text strings.

    Args:
        texts: List of text strings to embed.
        model_name: Optional model name override.

    Returns:
        List of embedding vectors (each a list of floats).
    """
    model = get_embedding_model(model_name)
    logger.debug(f"Generating embeddings for {len(texts)} text chunks")
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


def generate_single_embedding(text: str, model_name: Optional[str] = None) -> List[float]:
    """Generate an embedding for a single text string.

    Args:
        text: Text string to embed.
        model_name: Optional model name override.

    Returns:
        Embedding vector as a list of floats.
    """
    return generate_embeddings([text], model_name)[0]
