"""
LLM Client Module
Handles communication with LLM APIs (OpenRouter, OpenAI, etc.).

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""

import requests
from .config import settings


def call_llm(
    prompt: str,
    max_tokens: int = None,
    model: str = None,
    timeout: int = None
) -> str:
    """
    Call the LLM API with a prompt.

    Args:
        prompt: The prompt to send to the LLM
        max_tokens: Maximum tokens in the response (default: from settings)
        model: Model to use (default: from settings)
        timeout: Request timeout in seconds (default: from settings)

    Returns:
        The LLM response text

    Raises:
        RuntimeError: If required settings are not configured or API call fails
    """
    # Validate configuration
    is_valid, errors = settings.validate()
    if not is_valid:
        error_msg = "LLM client not properly configured:\n  - " + "\n  - ".join(errors)
        error_msg += "\n\nCheck your .env file (see .env.example for template)"
        raise RuntimeError(error_msg)

    # Use provided values or defaults from settings
    selected_model = model or settings.LLM_DEFAULT_MODEL
    selected_max_tokens = max_tokens or settings.LLM_MAX_TOKENS
    selected_timeout = timeout or settings.LLM_TIMEOUT

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    # Chat completions format (OpenRouter, OpenAI compatible)
    body = {
        "model": selected_model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": selected_max_tokens
    }

    try:
        resp = requests.post(
            settings.LLM_ENDPOINT,
            headers=headers,
            json=body,
            timeout=selected_timeout
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.Timeout as e:
        raise RuntimeError(
            f"LLM call timed out after {selected_timeout}s. "
            f"Consider increasing LLM_TIMEOUT in .env"
        ) from e
    except requests.RequestException as e:
        raise RuntimeError(f"LLM HTTP error: {e} - response: {getattr(e, 'response', None)}") from e
    except ValueError as e:
        raise RuntimeError(f"Failed to parse JSON from LLM response: {e}") from e

    # Extract the response from chat completion format
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected LLM response format: {data}") from e
