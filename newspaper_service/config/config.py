"""
Configuration management for newspaper service.
"""

import os
from pathlib import Path
from typing import Optional

import yaml


class Config:
    """Configuration class for newspaper service."""

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

        Args:
            config_dir: Directory containing config files

        Returns:
            Path to the appropriate config file

        Raises:
            ValueError: If environment is not 'local' or 'production'
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

    @property
    def service_name(self) -> str:
        """Get service name."""
        return self._config_data.get("service", {}).get(
            "service_name", "newspaper-service"
        )

    @property
    def service_port(self) -> int:
        """Get service port."""
        return self._config_data.get("service", {}).get("service_port", 8003)

    @property
    def user_service_base_url(self) -> str:
        """Get user service base URL."""
        return (
            self._config_data.get("external", {})
            .get("user_service", {})
            .get("base_url", "http://localhost")
        )

    @property
    def user_service_port(self) -> int:
        """Get user service port."""
        return (
            self._config_data.get("external", {})
            .get("user_service", {})
            .get("port", 8000)
        )

    @property
    def user_service_url(self) -> str:
        """Get complete user service URL."""
        # Don't append port for default HTTPS (443) or HTTP (80) ports
        if (
            self.user_service_base_url.startswith("https://")
            and int(self.user_service_port) == 443
        ) or (
            self.user_service_base_url.startswith("http://")
            and int(self.user_service_port) == 80
        ):
            return self.user_service_base_url
        return f"{self.user_service_base_url}:{self.user_service_port}"

    @property
    def user_service_timeout(self) -> float:
        """Get user service timeout in seconds."""
        return (
            self._config_data.get("external", {})
            .get("user_service", {})
            .get("timeout", 120.0)  # Default 2 minutes
        )

    def get(self, key: str, default=None):
        """Get configuration value by key using dot notation."""
        keys = key.split(".")
        value = self._config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value
