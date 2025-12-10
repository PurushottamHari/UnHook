#!/usr/bin/env python3
"""
Test script for the modified article_processor.py to verify local marketing frontend integration.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.daily_disciple.article_processor import ArticleProcessor


def test_local_app_startup_shutdown():
    """Test the local marketing frontend startup and shutdown functionality."""
    print("Testing local marketing frontend startup and shutdown...")
    
    processor = ArticleProcessor()
    
    try:
        # Test startup
        print("\n1. Testing app startup...")
        success = processor.start_local_marketing_frontend()
        
        if success:
            print("✅ App started successfully")
            
            # Test shutdown
            print("\n2. Testing app shutdown...")
            processor.stop_local_marketing_frontend()
            print("✅ App stopped successfully")
        else:
            print("❌ App failed to start")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        processor.close_connections()

def test_api_calls_with_dummy_article():
    """Test API calls with a dummy article ID."""
    print("\nTesting API calls with dummy article ID...")
    
    processor = ArticleProcessor()
    
    try:
        # Use a dummy article ID for testing
        dummy_article_id = "test-article-id-12345"
        processor.make_api_calls(dummy_article_id)
        print("✅ API calls test completed")
        
    except Exception as e:
        print(f"❌ API calls test failed with error: {e}")
    finally:
        processor.close_connections()

if __name__ == "__main__":
    print("🧪 Testing Article Processor with Local Marketing Frontend Integration")
    print("=" * 70)
    
    # Test 1: Local app startup/shutdown
    test_local_app_startup_shutdown()
    
    # Test 2: API calls (this will test the full flow)
    test_api_calls_with_dummy_article()
    
    print("\n" + "=" * 70)
    print("🏁 All tests completed!")
