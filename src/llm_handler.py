"""
LLM Handler Module

Manages communication with the Groq API using the Groq Python SDK.
Handles client initialization, prompt formatting, and response generation.
"""

import os
from typing import Optional, Generator

from groq import Groq
from dotenv import load_dotenv

load_dotenv()


# Default model configuration
DEFAULT_MODEL = "llama-3.3-70b-versatile"

_client_cache: Optional[Groq] = None


def get_client(api_key: Optional[str] = None) -> Groq:
    """Get or initialize the Groq API client (cached singleton).

    Args:
        api_key: Groq API key. Falls back to GROQ_API_KEY env var.

    Returns:
        Configured Groq client.

    Raises:
        ValueError: If no API key is provided or found.
    """
    global _client_cache

    if _client_cache is None:
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError(
                "Groq API key is required. Set GROQ_API_KEY in .env or pass it directly."
            )
        _client_cache = Groq(api_key=key)

    return _client_cache


def get_model_name(model_name: Optional[str] = None) -> str:
    """Resolve the model name from argument or environment.

    Args:
        model_name: Optional model name override.

    Returns:
        Resolved model name string.
    """
    return model_name or os.getenv("LLM_MODEL", DEFAULT_MODEL)


def generate_response(
    prompt: str,
    model_name: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """Generate a response from the Groq model.

    Args:
        prompt: The formatted prompt to send.
        model_name: Optional model name override.
        temperature: Sampling temperature (0.0 - 1.0).
        max_tokens: Maximum tokens in the response.

    Returns:
        Generated text response.
    """
    client = get_client()
    model = get_model_name(model_name)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content


def generate_response_stream(
    prompt: str,
    model_name: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> Generator[str, None, None]:
    """Generate a streaming response from the Groq model.

    Args:
        prompt: The formatted prompt to send.
        model_name: Optional model name override.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens in the response.

    Yields:
        Text chunks as they are generated.
    """
    client = get_client()
    model = get_model_name(model_name)

    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content


def test_connection() -> bool:
    """Test the Groq API connection.

    Returns:
        True if connection is successful, False otherwise.
    """
    try:
        response = generate_response("Say 'connected' in one word.")
        return "connected" in response.lower()
    except Exception:
        return False
