"""
Configuration settings for the UnHook Scrappy Frontend App.
"""

import os
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    "MONGODB_URI": "mongodb+srv://purushottam:test12345@cluster0.xv0gfbm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "DATABASE_NAME": "youtube_newspaper",
    "FLASK_DEBUG": True,
    "FLASK_HOST": "0.0.0.0",
    "FLASK_PORT": 5001,
}


def get_config():
    """Get configuration with environment variable overrides."""
    config = DEFAULT_CONFIG.copy()

    # Override with environment variables
    for key in config:
        env_value = os.getenv(key)
        if env_value is not None:
            config[key] = env_value

    # Convert port to int
    config["FLASK_PORT"] = int(config["FLASK_PORT"])

    # Convert FLASK_DEBUG to boolean
    debug_value = config["FLASK_DEBUG"]
    if isinstance(debug_value, str):
        config["FLASK_DEBUG"] = debug_value.lower() in ("true", "1", "yes")
    else:
        config["FLASK_DEBUG"] = bool(debug_value)

    return config


# Load configuration
CONFIG = get_config()
