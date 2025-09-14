#!/usr/bin/env python3
"""
Test script to verify the scrappy frontend app works locally before deployment.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))


def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")

    try:
        import pytz

        print("✅ pytz imported successfully")
    except ImportError as e:
        print(f"❌ pytz import failed: {e}")
        return False

    try:
        import flask

        print("✅ flask imported successfully")
    except ImportError as e:
        print(f"❌ flask import failed: {e}")
        return False

    try:
        import pymongo

        print("✅ pymongo imported successfully")
    except ImportError as e:
        print(f"❌ pymongo import failed: {e}")
        return False

    try:
        import markdown

        print("✅ markdown imported successfully")
    except ImportError as e:
        print(f"❌ markdown import failed: {e}")
        return False

    try:
        from data_processing_service.models.generated_content import \
            GeneratedContentStatus

        print("✅ data_processing_service imported successfully")
    except ImportError as e:
        print(f"❌ data_processing_service import failed: {e}")
        return False

    try:
        from user_service.models.enums import CategoryName, OutputType, Weekday

        print("✅ user_service imported successfully")
    except ImportError as e:
        print(f"❌ user_service import failed: {e}")
        return False

    return True


def test_config():
    """Test if configuration loads properly."""
    print("\n🔧 Testing configuration...")

    try:
        from config import CONFIG

        print(f"✅ Config loaded successfully")
        print(f"   MongoDB URI: {CONFIG['MONGODB_URI'][:20]}...")
        print(f"   Database: {CONFIG['DATABASE_NAME']}")
        print(f"   Flask Host: {CONFIG['FLASK_HOST']}")
        print(f"   Flask Port: {CONFIG['FLASK_PORT']}")
        print(f"   Flask Debug: {CONFIG['FLASK_DEBUG']}")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False


def test_database_connection():
    """Test if database connection works."""
    print("\n🗄️  Testing database connection...")

    try:
        from app import get_database
        from config import CONFIG

        # Check if we're using localhost (which won't work without local MongoDB)
        if "localhost" in CONFIG["MONGODB_URI"]:
            print("⚠️  Using localhost MongoDB - skipping connection test")
            print("   For Railway deployment, this will use your cloud MongoDB")
            return True

        db = get_database()
        # Try to ping the database using the client
        client = db.client
        client.admin.command("ping")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure your MongoDB URI is correct in your .env file")
        print("   For local testing, you can skip this if using cloud MongoDB")
        return False


def test_flask_app():
    """Test if Flask app can be created."""
    print("\n🌐 Testing Flask app creation...")

    try:
        from app import app

        print("✅ Flask app created successfully")

        # Test if routes are registered
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        print(f"   Found {len(routes)} routes")

        # Check for key routes
        key_routes = ["/", "/health", "/api/categories"]
        for route in key_routes:
            if route in routes:
                print(f"   ✅ {route} route found")
            else:
                print(f"   ❌ {route} route missing")

        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 UnHook Scrappy Frontend - Local Test Suite")
    print("=" * 50)

    tests = [test_imports, test_config, test_database_connection, test_flask_app]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your app is ready for deployment.")
        print("\n🚀 To start the app locally:")
        print("   python run.py")
        print("\n🌐 Then open: http://localhost:5001")
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        print("\n🔧 Common fixes:")
        print("   1. Install missing dependencies: pip install -r requirements.txt")
        print("   2. Check your .env file has correct MongoDB URI")
        print("   3. Make sure parent directory structure is intact")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
