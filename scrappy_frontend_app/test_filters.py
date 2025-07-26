#!/usr/bin/env python3
"""
Test script to verify the new filter functionality in the scrappy frontend app.
"""

import sys
import os

# Add the parent directory to the path to import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import fetch_articles, get_unique_categories

def test_filters():
    """Test the new filter functionality."""
    print("Testing UnHook Frontend App Filters")
    print("=" * 40)
    
    try:
        # Test getting unique categories
        print("1. Testing get_unique_categories()...")
        categories = get_unique_categories()
        print(f"   Found {len(categories)} unique categories: {categories}")
        
        # Test fetching articles with no filters
        print("\n2. Testing fetch_articles() with no filters...")
        articles = fetch_articles("default_user", "newest")
        print(f"   Found {len(articles)} articles")
        
        # Test fetching articles with category filter (if categories exist)
        if categories:
            print(f"\n3. Testing fetch_articles() with category filter '{categories[0]}'...")
            filtered_articles = fetch_articles("default_user", "newest", category_filter=categories[0])
            print(f"   Found {len(filtered_articles)} articles with category '{categories[0]}'")
        
        # Test fetching articles with content type filter
        print("\n4. Testing fetch_articles() with content type filter 'MEDIUM'...")
        medium_articles = fetch_articles("default_user", "newest", content_type_filter="MEDIUM")
        print(f"   Found {len(medium_articles)} articles with MEDIUM content type")
        
        print("\n5. Testing fetch_articles() with content type filter 'LONG'...")
        long_articles = fetch_articles("default_user", "newest", content_type_filter="LONG")
        print(f"   Found {len(long_articles)} articles with LONG content type")
        
        # Test combined filters
        if categories:
            print(f"\n6. Testing fetch_articles() with combined filters (category: {categories[0]}, content_type: MEDIUM)...")
            combined_articles = fetch_articles("default_user", "newest", category_filter=categories[0], content_type_filter="MEDIUM")
            print(f"   Found {len(combined_articles)} articles with both filters")
        
        print("\n✅ All filter tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_filters() 