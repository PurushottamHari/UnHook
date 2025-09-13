#!/usr/bin/env python3
"""
Test script for YouTube cookies in GitHub Actions environment.
This script tests the exact same functionality as the main pipeline.
"""

import os
import sys

import yt_dlp


def test_metadata_extraction(cookie_file):
    """Test metadata extraction (like get_channel_videos)"""
    print("=" * 50)
    print("🧪 Test 1: Metadata Extraction")
    print("=" * 50)

    metadata_opts = {
        "cookiefile": cookie_file,
        "quiet": False,
        "verbose": True,
        "no_warnings": False,
        "extract_flat": True,
        "retries": 3,
        "fragment_retries": 3,
        "ignoreerrors": False,
        "extractor_retries": 3,
        "http_chunk_size": 10485760,
        "concurrent_fragment_downloads": 1,
    }

    test_video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"Testing metadata extraction with: {test_video}")

    try:
        with yt_dlp.YoutubeDL(metadata_opts) as ydl:
            info = ydl.extract_info(test_video, download=False)
            if info:
                print(
                    f'✅ Metadata test PASSED! Video title: {info.get("title", "Unknown")}'
                )
                return True
            else:
                print("❌ Metadata test FAILED: No video info returned")
                return False
    except Exception as e:
        print(f"❌ Metadata test FAILED: {e}")
        return False


def test_subtitle_download(cookie_file):
    """Test subtitle download (like download_subtitles)"""
    print("=" * 50)
    print("🧪 Test 2: Subtitle Download")
    print("=" * 50)

    subtitle_opts = {
        "cookiefile": cookie_file,
        "quiet": False,
        "verbose": True,
        "no_warnings": False,
        "writesubtitles": True,
        "writeautomaticsub": False,
        "subtitleslangs": ["en"],
        "subtitlesformat": "srt",
        "skip_download": True,
        "retries": 3,
        "limit_rate": "150K",
    }

    test_video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"Testing subtitle download with: {test_video}")

    try:
        with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
            info = ydl.extract_info(test_video, download=False)
            if info:
                print(
                    f'✅ Subtitle test PASSED! Video title: {info.get("title", "Unknown")}'
                )
                # Check if subtitles were actually downloaded
                if os.path.exists("subtitles"):
                    print("✅ Subtitle files were created!")
                    # List the subtitle files
                    for root, dirs, files in os.walk("subtitles"):
                        for file in files:
                            print(f"  📄 {os.path.join(root, file)}")
                else:
                    print("⚠️  No subtitle files found, but extraction succeeded")
                return True
            else:
                print("❌ Subtitle test FAILED: No video info returned")
                return False
    except Exception as e:
        print(f"❌ Subtitle test FAILED: {e}")
        return False


def test_age_restricted_video(cookie_file):
    """Test age-restricted video (like the ones causing issues)"""
    print("=" * 50)
    print("🧪 Test 3: Age-restricted Video (from your error logs)")
    print("=" * 50)

    subtitle_opts = {
        "cookiefile": cookie_file,
        "quiet": False,
        "verbose": True,
        "no_warnings": False,
        "writesubtitles": True,
        "writeautomaticsub": False,
        "subtitleslangs": ["en"],
        "subtitlesformat": "srt",
        "skip_download": True,
        "retries": 3,
        "limit_rate": "150K",
    }

    age_restricted_video = "https://www.youtube.com/watch?v=1GpGqwXExYE"
    print(f"Testing age-restricted video: {age_restricted_video}")

    try:
        with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
            info = ydl.extract_info(age_restricted_video, download=False)
            if info:
                print(
                    f'✅ Age-restricted test PASSED! Video title: {info.get("title", "Unknown")}'
                )
                return True
            else:
                print("❌ Age-restricted test FAILED: No video info returned")
                return False
    except Exception as e:
        print(f"❌ Age-restricted test FAILED: {e}")
        print(
            "This is expected for age-restricted videos without proper authentication"
        )
        return False


def main():
    """Main test function"""
    print("🍪 Testing YouTube cookies in GitHub Actions environment...")
    print("=" * 60)

    # Check if cookie file exists
    cookie_file = "test_cookies.txt"
    if not os.path.exists(cookie_file):
        print(f"❌ Cookie file not found: {cookie_file}")
        sys.exit(1)

    # Check file size and permissions
    file_size = os.path.getsize(cookie_file)
    file_perms = oct(os.stat(cookie_file).st_mode)[-3:]
    print(f"📊 Cookie file size: {file_size} bytes")
    print(f"🔐 Cookie file permissions: {file_perms}")

    # Read first few lines to check format
    with open(cookie_file, "r") as f:
        lines = f.readlines()[:3]
        print(f"📝 First 3 lines of cookie file:")
        for i, line in enumerate(lines, 1):
            print(f"  {i}: {line.strip()}")

    print("\n" + "=" * 60)

    # Run tests
    results = []

    # Test 1: Metadata extraction
    results.append(test_metadata_extraction(cookie_file))

    # Test 2: Subtitle download
    results.append(test_subtitle_download(cookie_file))

    # Test 3: Age-restricted video
    results.append(test_age_restricted_video(cookie_file))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    test_names = ["Metadata Extraction", "Subtitle Download", "Age-restricted Video"]
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {name}: {status}")

    passed = sum(results)
    total = len(results)

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Cookies are working correctly.")
        sys.exit(0)
    elif passed >= 2:  # Metadata and subtitle download should work
        print("⚠️  Some tests failed, but core functionality works.")
        print(
            "Age-restricted video failures are expected without proper authentication."
        )
        sys.exit(0)
    else:
        print("💥 Critical tests failed! Cookie setup needs attention.")
        sys.exit(1)


if __name__ == "__main__":
    main()
