#!/usr/bin/env python3
"""
Test script for YouTube cookies in GitHub Actions environment.
This script tests the exact same functionality as the main pipeline.
"""

import os
import sys

import yt_dlp


def test_subtitle_download(cookie_file):
    """Test subtitle download with 3 retries"""
    print("=" * 50)
    print("🧪 Testing Subtitle Download")
    print("=" * 50)

    subtitle_opts = {
        "cookiefile": cookie_file,
        "quiet": False,
        "verbose": True,
        "no_warnings": False,
        "writesubtitles": True,
        "writeautomaticsub": True,  # Also try automatic subtitles
        "subtitleslangs": ["en"],
        "subtitlesformat": "srt",
        "skip_download": True,
        "retries": 3,
        "limit_rate": "150K",
    }

    test_video = "https://www.youtube.com/watch?v=1GpGqwXExYE"
    print(f"Testing subtitle download with: {test_video}")

    for attempt in range(1, 4):  # 3 attempts
        print(f"\n🔄 Attempt {attempt}/3")
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
                        return True
                    else:
                        print("⚠️  No subtitle files found, but extraction succeeded")
                        return True
                else:
                    print("❌ Subtitle test FAILED: No video info returned")
        except Exception as e:
            print(f"❌ Attempt {attempt} FAILED: {e}")
            if attempt < 3:
                print("🔄 Retrying...")
            else:
                print("💥 All 3 attempts failed!")
                return False

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

    # Run subtitle download test
    result = test_subtitle_download(cookie_file)

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    status = "✅ PASSED" if result else "❌ FAILED"
    print(f"Subtitle Download: {status}")

    if result:
        print("🎉 Subtitle download test passed! Cookies are working correctly.")
        sys.exit(0)
    else:
        print("💥 Subtitle download test failed! Cookie setup needs attention.")
        sys.exit(1)


if __name__ == "__main__":
    main()
