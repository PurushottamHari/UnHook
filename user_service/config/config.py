"""
Configuration management for user service.
"""

import os
from pathlib import Path
from typing import Optional

import yaml


class Config:
    """
    Configuration class for user service.

    CRITICAL PHILOSOPHY: Never use fallbacks or default values for configuration.
    If a configuration key is missing, the service MUST fail fast and raise an error
    on startup to avoid unpredictable behavior in different environments.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to config file. If None, uses environment-based config.
        """
        if config_path is None:
            # Get the directory where this config.py file is located
            current_dir = Path(__file__).parent
            config_path = self._get_config_path(current_dir)

        self.config_path = Path(config_path)
        self._config_data = self._load_config()

    def _get_config_path(self, config_dir: Path) -> Path:
        """
        Get the appropriate config file path based on environment variable.
        """
        environment = os.getenv("environment", "local").lower()

        if environment == "local":
            return config_dir / "local_config.yaml"
        elif environment == "production":
            return config_dir / "prod_config.yaml"
        else:
            raise ValueError(
                f"Invalid environment '{environment}'. Must be 'local' or 'production'"
            )

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def get(self, key: str):
        """
        Get configuration value by key using dot notation.

        Raises:
            ValueError: If the key is missing from the configuration.
        """
        keys = key.split(".")
        value = self._config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                raise ValueError(
                    f"CRITICAL CONFIGURATION ERROR: Key '{key}' is missing in {self.config_path}. "
                    "Service cannot start without all required configurations."
                )

        if value is None:
            raise ValueError(
                f"CRITICAL CONFIGURATION ERROR: Key '{key}' is defined but has no value in {self.config_path}."
            )

        return value

    @property
    def service_name(self) -> str:
        """Get service name."""
        return self.get("service.service_name")

    @property
    def service_port(self) -> int:
        """Get service port, prioritizing PORT environment variable."""
        env_port = os.getenv("PORT")
        if env_port:
            print("PORT FROM ENV:", env_port)
            return int(env_port)
        return self.get("service.service_port")

    @property
    def mongodb_uri(self) -> str:
        """Get MongoDB URI."""
        return self.get("mongodb.uri")

    @property
    def database_name(self) -> str:
        """Get database name."""
        return self.get("mongodb.database_name")

    @property
    def user_service_url(self) -> str:
        """Get complete user service URL (for internal consistency)."""
        # User service usually just needs its own port for binding,
        # but this might be used for generating self-referential links.
        return f"http://localhost:{self.service_port}"
