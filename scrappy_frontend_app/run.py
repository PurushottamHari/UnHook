#!/usr/bin/env python3
"""
Simple startup script for the UnHook Scrappy Frontend App.
"""

import os
import sys
from pathlib import Path

# Handle both local development and Railway deployment
current_dir = Path(__file__).parent
if current_dir.name == "scrappy_frontend_app":
    # Running from scrappy_frontend_app directory (local development)
    parent_dir = current_dir.parent
    sys.path.insert(0, str(parent_dir))
    os.chdir(current_dir)  # Change to scrappy_frontend_app directory
else:
    # Running from repository root (Railway deployment)
    scrappy_dir = current_dir / "scrappy_frontend_app"
    if scrappy_dir.exists():
        sys.path.insert(0, str(current_dir))
        os.chdir(scrappy_dir)  # Change to scrappy_frontend_app directory
    else:
        # Fallback: assume we're already in the right directory
        pass

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
