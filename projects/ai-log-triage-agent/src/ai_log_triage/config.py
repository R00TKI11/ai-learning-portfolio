"""
Configuration Module
Manages environment variables and application settings.

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Loads .env file automatically


class Settings:
    """
    Centralized application settings.

    All configuration is loaded from environment variables.
    See .env.example for configuration template.
    """

    # ============================================================================
    # LLM API Configuration
    # ============================================================================

    # Required: API credentials
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY")
    LLM_ENDPOINT: Optional[str] = os.getenv("LLM_ENDPOINT")

    # Required: Default model to use
    LLM_DEFAULT_MODEL: Optional[str] = os.getenv("LLM_DEFAULT_MODEL")

    # Optional: Request timeout in seconds (default: 120)
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "120"))

    # Optional: Max tokens for LLM responses (default: 1024)
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1024"))

    # ============================================================================
    # Application Configuration
    # ============================================================================

    # Data directory for log files
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")

    # ============================================================================
    # Validation
    # ============================================================================

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate that required settings are configured.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY is not set")

        if not cls.LLM_ENDPOINT:
            errors.append("LLM_ENDPOINT is not set")

        if not cls.LLM_DEFAULT_MODEL:
            errors.append("LLM_DEFAULT_MODEL is not set")

        if cls.LLM_TIMEOUT <= 0:
            errors.append(f"LLM_TIMEOUT must be positive (got {cls.LLM_TIMEOUT})")

        if cls.LLM_MAX_TOKENS <= 0:
            errors.append(f"LLM_MAX_TOKENS must be positive (got {cls.LLM_MAX_TOKENS})")

        return (len(errors) == 0, errors)

    @classmethod
    def is_configured(cls) -> bool:
        """Check if minimum required settings are configured."""
        return bool(cls.LLM_API_KEY and cls.LLM_ENDPOINT and cls.LLM_DEFAULT_MODEL)


# Global settings instance
settings = Settings()
