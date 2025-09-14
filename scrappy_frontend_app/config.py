"""
Configuration settings for the UnHook Scrappy Frontend App.
"""

import os
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    "MONGODB_URI": os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
    "DATABASE_NAME": os.getenv("DATABASE_NAME", "youtube_newspaper"),
    "FLASK_DEBUG": os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes"),
    "FLASK_HOST": os.getenv("FLASK_HOST", "0.0.0.0"),
    "FLASK_PORT": int(os.getenv("FLASK_PORT", "5001")),
}


def get_config():
    """Get configuration with environment variable overrides."""
    return DEFAULT_CONFIG.copy()


# Load configuration
CONFIG = get_config()
