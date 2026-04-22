"""
Configuration management for data collector service.
"""

import os
from pathlib import Path
from typing import Optional

import yaml


class Config:
    """Configuration class for data collector service."""

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
        environment = os.getenv("environment").lower()

        if environment == "local":
            print(f"[Config] Loading local config")
            return config_dir / "local_config.yaml"
        elif environment == "production":
            print(f"[Config] Loading production config")
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
            "service_name", "data_collector_service"
        )

    @property
    def service_port(self) -> int:
        """Get service port."""
        return self._config_data.get("service", {}).get("service_port", 8001)

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

    @property
    def proxy_base_url(self) -> str:
        """Get proxy base URL."""
        return self._config_data.get("proxy", {}).get("base_url", "api.zyte.com:8011")

    @property
    def redis_host(self) -> str:
        """Get Redis host."""
        return self._config_data.get("redis", {}).get("host", "localhost")

    @property
    def redis_port(self) -> int:
        """Get Redis port."""
        return self._config_data.get("redis", {}).get("port", 6379)

    @property
    def redis_db(self) -> int:
        """Get Redis database index."""
        return self._config_data.get("redis", {}).get("db", 0)

    @property
    def messaging_command_topic(self) -> str:
        """Get the main command topic for this service."""
        return f"{self.service_name}.commands"

    # S3 / R2 Configuration
    @property
    def s3_access_key_id(self) -> str:
        """Fetches S3 access key from environment variables. Required."""
        val = os.getenv("R2_ACCESS_KEY_ID")
        if not val:
            raise ValueError("R2_ACCESS_KEY_ID environment variable is not set")
        return val

    @property
    def s3_secret_access_key(self) -> str:
        """Fetches S3 secret key from environment variables. Required."""
        val = os.getenv("R2_SECRET_ACCESS_KEY")
        if not val:
            raise ValueError("R2_SECRET_ACCESS_KEY environment variable is not set")
        return val

    @property
    def s3_account_id(self) -> str:
        """Fetches R2 account ID from config."""
        return self._config_data.get("s3").get("account_id")

    @property
    def s3_bucket_name(self) -> str:
        """Fetches R2 bucket name from config."""
        return self._config_data.get("s3").get("bucket_name")

    @property
    def s3_endpoint_url(self) -> str:
        """Fetches S3 endpoint URL from config."""
        return self._config_data.get("s3").get("endpoint_url")

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
