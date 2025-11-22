"""
LLM Client Module
Handles communication with the OpenRouter API.

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""

import requests
from .config import settings

API_KEY = settings.LLM_OPENROUTER_API_KEY
ENDPOINT = settings.LLM_ENDPOINT
DEFAULT_MODEL = settings.LLM_DEFAULT_MODEL

def call_llm(prompt: str, max_tokens: int = 1024, model: str = None) -> str:
    """
    Call the LLM API with a prompt.

    Args:
        prompt: The prompt to send to the LLM
        max_tokens: Maximum tokens in the response
        model: Model to use (defaults to MODEL from env)

    Returns:
        The LLM response text

    Raises:
        RuntimeError: If required environment variables are not set
    """
    if not API_KEY or not ENDPOINT:
        raise RuntimeError(
            "LLM_OPENROUTER_API_KEY or LLM_ENDPOINT is not set. "
            "Check your .env file or environment variables."
        )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Use provided model or default from settings
    selected_model = model or DEFAULT_MODEL

    if not selected_model:
        raise RuntimeError(
            "No LLM model specified and LLM_DEFAULT_MODEL is not set in .env. "
            "Either pass a model parameter or set a default model in your .env file."
        )

    # OpenRouter uses chat completions format
    body = {
        "model": selected_model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_tokens
    }

    try:
        resp = requests.post(ENDPOINT, headers=headers, json=body, timeout=120) #set timeout to 120 but might want to add this as a CLI argument in the future
        resp.raise_for_status()
        data = resp.json()
    except requests.Timeout as e:
        raise RuntimeError(f"LLM call timed out: {e}") from e
    except requests.RequestException as e:
        raise RuntimeError(f"LLM HTTP error: {e} - response: {getattr(e, 'response', None)}") from e
    except ValueError as e:
        raise RuntimeError(f"Failed to parse JSON from LLM response: {e}") from e

    # Extract the response from chat completion format
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected LLM response format: {data}") from e
