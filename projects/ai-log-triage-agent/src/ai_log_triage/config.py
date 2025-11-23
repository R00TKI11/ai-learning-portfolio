"""
Configuration Module
Manages environment variables, application settings, and configuration profiles.

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()  # Loads .env file automatically


class ProfileManager:
    """Manages configuration profiles for different use cases."""

    @staticmethod
    def get_profiles_dir() -> Path:
        """Get the profiles directory path."""
        # Check if running from installed package or development
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        profiles_dir = project_root / "profiles"

        if not profiles_dir.exists():
            # Fallback to relative path
            profiles_dir = Path("profiles")

        return profiles_dir

    @staticmethod
    def list_profiles() -> list[str]:
        """List all available profile names."""
        profiles_dir = ProfileManager.get_profiles_dir()
        if not profiles_dir.exists():
            return []

        profiles = []
        for file in profiles_dir.glob("*.yaml"):
            profiles.append(file.stem)

        return sorted(profiles)

    @staticmethod
    def load_profile(profile_name: str) -> Dict[str, Any]:
        """
        Load a configuration profile from YAML file.

        Args:
            profile_name: Name of the profile (without .yaml extension)

        Returns:
            Dictionary with profile configuration

        Raises:
            FileNotFoundError: If profile doesn't exist
            ValueError: If profile is invalid
        """
        profiles_dir = ProfileManager.get_profiles_dir()
        profile_path = profiles_dir / f"{profile_name}.yaml"

        if not profile_path.exists():
            available = ProfileManager.list_profiles()
            raise FileNotFoundError(
                f"Profile '{profile_name}' not found. "
                f"Available profiles: {', '.join(available) if available else 'none'}"
            )

        try:
            with open(profile_path, 'r') as f:
                profile_data = yaml.safe_load(f)

            if not isinstance(profile_data, dict):
                raise ValueError(f"Profile '{profile_name}' has invalid format")

            return profile_data
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing profile '{profile_name}': {e}")

    @staticmethod
    def get_profile_info(profile_name: str) -> Optional[Dict[str, str]]:
        """
        Get basic information about a profile without loading full config.

        Returns:
            Dictionary with 'name' and 'description', or None if not found
        """
        try:
            profile_data = ProfileManager.load_profile(profile_name)
            return {
                'name': profile_data.get('name', profile_name),
                'description': profile_data.get('description', 'No description')
            }
        except (FileNotFoundError, ValueError):
            return None


class Settings:
    """
    Centralized application settings.

    Configuration is loaded from:
    1. Environment variables (.env file)
    2. Configuration profiles (profiles/*.yaml)
    3. Runtime overrides (CLI arguments)

    Profiles are loaded with load_profile() and override defaults.
    See .env.example for environment variable configuration.
    See profiles/ directory for profile examples.
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

    # Optional: Temperature for LLM responses (default: 0.5)
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.5"))

    # ============================================================================
    # Application Configuration
    # ============================================================================

    # Data directory for log files
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")

    # Log truncation settings
    TRUNCATE_LOGS: bool = os.getenv("TRUNCATE_LOGS", "true").lower() == "true"
    MAX_LOG_LENGTH: int = int(os.getenv("MAX_LOG_LENGTH", "5000"))

    # Current profile name (if loaded)
    _current_profile: Optional[str] = None

    # ============================================================================
    # Profile Management
    # ============================================================================

    @classmethod
    def load_profile(cls, profile_name: str) -> None:
        """
        Load configuration from a profile and apply to settings.

        Args:
            profile_name: Name of the profile to load

        Raises:
            FileNotFoundError: If profile doesn't exist
            ValueError: If profile is invalid
        """
        profile_data = ProfileManager.load_profile(profile_name)

        # Apply LLM configuration
        if 'llm' in profile_data:
            llm_config = profile_data['llm']

            if 'model' in llm_config:
                cls.LLM_DEFAULT_MODEL = llm_config['model']

            if 'max_tokens' in llm_config:
                cls.LLM_MAX_TOKENS = int(llm_config['max_tokens'])

            if 'timeout' in llm_config:
                cls.LLM_TIMEOUT = int(llm_config['timeout'])

            if 'temperature' in llm_config:
                cls.LLM_TEMPERATURE = float(llm_config['temperature'])

            # Override endpoint if specified in profile
            if 'endpoint' in llm_config:
                cls.LLM_ENDPOINT = llm_config['endpoint']

            # Override API key if specified in profile
            if 'api_key' in llm_config and llm_config['api_key']:
                cls.LLM_API_KEY = llm_config['api_key']

        # Apply application configuration
        if 'truncate_logs' in profile_data:
            cls.TRUNCATE_LOGS = bool(profile_data['truncate_logs'])

        if 'max_log_length' in profile_data:
            cls.MAX_LOG_LENGTH = int(profile_data['max_log_length'])

        cls._current_profile = profile_name

    @classmethod
    def get_current_profile(cls) -> Optional[str]:
        """Get the name of the currently loaded profile."""
        return cls._current_profile

    @classmethod
    def list_profiles(cls) -> list[str]:
        """List all available profile names."""
        return ProfileManager.list_profiles()

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
