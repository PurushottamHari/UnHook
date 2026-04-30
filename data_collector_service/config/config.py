"""
Configuration management for data collector service.
"""

import os
from pathlib import Path
from typing import Optional

import yaml


class Config:
    """
    Configuration class for data collector service.

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
        """Get service port."""
        return self.get("service.service_port")

    @property
    def user_service_base_url(self) -> str:
        """Get user service base URL, prioritizing environment variable."""
        return os.getenv(
            "USER_SERVICE_BASE_URL", self.get("external.user_service.base_url")
        )

    @property
    def user_service_port(self) -> int:
        """Get user service port, prioritizing environment variable."""
        env_port = os.getenv("USER_SERVICE_PORT")
        if env_port:
            return int(env_port)
        return self.get("external.user_service.port")

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
        return self.get("external.user_service.timeout")

    @property
    def proxy_base_url(self) -> str:
        """Get proxy base URL."""
        return self.get("proxy.base_url")

    @property
    def redis_url(self) -> str:
        """Get Redis URL, prioritizing environment variable."""
        env_url = os.getenv("REDIS_URL")
        if env_url:
            return env_url
        raise ValueError(
            "CRITICAL CONFIGURATION ERROR: REDIS_URL environment variable is not set. Service cannot start without Redis."
        )

    @property
    def messaging_command_topic(self) -> str:
        """Get the main command topic for this service."""
        return f"{self.service_name}:commands"

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
        return self.get("s3.account_id")

    @property
    def s3_bucket_name(self) -> str:
        """Fetches R2 bucket name from config."""
        return self.get("s3.bucket_name")

    @property
    def s3_endpoint_url(self) -> str:
        """Fetches S3 endpoint URL from config."""
        return self.get("s3.endpoint_url")

    @property
    def data_collector_service_topic(self) -> str:
        """Get the command topic for the data collection service."""
        return self.get("messaging.commands.data_collector_service.topic")

    @property
    def data_processing_service_topic(self) -> str:
        """Get the command topic for the data processing service."""
        return self.get("messaging.commands.data_processing_service.topic")

    @property
    def data_collector_service_events_topic(self) -> str:
        """Get the event topic for the data collector service."""
        return self.get("messaging.events.data_collector_service.topic")

    @property
    def data_processing_service_events_topic(self) -> str:
        """Get the event topic for the data processing service."""
        return self.get("messaging.events.data_processing_service.topic")
