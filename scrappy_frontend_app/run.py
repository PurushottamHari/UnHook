#!/usr/bin/env python3
"""
Simple startup script for the UnHook Scrappy Frontend App.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import and run the Flask app
from app import app
from config import CONFIG

if __name__ == "__main__":
    print("🚀 Starting UnHook Scrappy Frontend App...")
    print(f"📊 MongoDB URI: {CONFIG['MONGODB_URI']}")
    print(f"🗄️  Database: {CONFIG['DATABASE_NAME']}")
    print(
        f"🌐 Server will be available at: http://{CONFIG['FLASK_HOST']}:{CONFIG['FLASK_PORT']}"
    )
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    try:
        app.run(
            debug=CONFIG["FLASK_DEBUG"],
            host=CONFIG["FLASK_HOST"],
            port=CONFIG["FLASK_PORT"],
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
