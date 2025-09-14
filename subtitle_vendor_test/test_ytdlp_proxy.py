#!/usr/bin/env python3
"""
Test script for yt-dlp with Zyte proxy support for YouTube subtitle downloading.
Tests subtitle downloading for specific video IDs using yt-dlp configured with Zyte proxy.
Uses yt-dlp's built-in proxy support with Zyte proxy configuration.
"""

import json
import os
import sys
import time
import traceback
from base64 import b64decode
from typing import Any, Dict, List, Optional

# Import the subtitle libraries
try:
    import yt_dlp

    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("⚠️  yt-dlp not available")

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests not available (needed for Zyte proxy)")


class ZyteProxyHandler:
    """Handler for Zyte proxy requests"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.zyte.com/v1/extract"

    def make_proxy_request(self, url: str) -> bytes:
        """Make a request through Zyte proxy and return response body"""
        try:
            api_response = requests.post(
                self.base_url,
                auth=(self.api_key, ""),
                json={
                    "url": url,
                    "httpResponseBody": True,
                    "followRedirect": True,
                },
                timeout=30,
            )

            if api_response.status_code == 200:
                response_data = api_response.json()
                if "httpResponseBody" in response_data:
                    return b64decode(response_data["httpResponseBody"])
                else:
                    raise Exception("No httpResponseBody in response")
            else:
                raise Exception(
                    f"Proxy request failed with status {api_response.status_code}"
                )

        except Exception as e:
            print(f"  ⚠️  Proxy request failed: {str(e)}")
            raise


class YtDlpProxyTester:
    """Test class for yt-dlp with Zyte proxy support"""

    def __init__(self, zyte_api_key: str):
        self.zyte_api_key = zyte_api_key
        self.zyte_proxy = ZyteProxyHandler(zyte_api_key)
        # Test with the specified video IDs
        self.test_videos = ["1GpGqwXExYE", "9uY6N2Bl0pU"]
        self.max_retries = 2
        self.results = {}
        # Set up proxy environment variables
        self._setup_proxy_environment()

    def _setup_proxy_environment(self):
        """Set up proxy environment variables like in command line"""
        zyte_proxy_url = f"http://{self.zyte_api_key}:@api.zyte.com:8011"
        os.environ["HTTP_PROXY"] = zyte_proxy_url
        os.environ["HTTPS_PROXY"] = zyte_proxy_url
        print(
            f"🌐 Set proxy environment: {zyte_proxy_url.replace(self.zyte_api_key, 'API_KEY_HIDDEN')}"
        )

    def test_proxy_connection(self) -> bool:
        """Test if the Zyte proxy connection is working with yt-dlp"""
        print("🔍 Testing Zyte proxy connection with yt-dlp...")
        try:
            test_opts = {
                "quiet": True,
                "no_warnings": True,
                "nocheckcertificate": True,  # Correct yt-dlp option name for --no-check-certificate
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
            }

            # Test with a simple YouTube video
            test_url = (
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short video
            )

            with yt_dlp.YoutubeDL(test_opts) as ydl:
                info = ydl.extract_info(test_url, download=False)
                if info and info.get("title"):
                    print("✅ Proxy connection successful with yt-dlp")
                    print(f"📄 Test video title: {info.get('title', 'Unknown')}")
                    return True
                else:
                    print("❌ Proxy connection failed - no video info returned")
                    return False

        except Exception as e:
            print(f"❌ Proxy connection failed: {str(e)}")
            return False

    def download_subtitles_with_proxy(self, video_id: str) -> Dict[str, Any]:
        """Download subtitles using yt-dlp with Zyte proxy"""
        print(f"\n🔧 Testing yt-dlp with Zyte proxy for video: {video_id}")

        if not YT_DLP_AVAILABLE:
            return {"success": False, "error": "yt-dlp not available", "attempts": 0}

        if not REQUESTS_AVAILABLE:
            return {"success": False, "error": "requests not available", "attempts": 0}

        for attempt in range(1, self.max_retries + 1):
            print(f"  🔄 Attempt {attempt}/{self.max_retries}")
            try:
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                print(
                    f"  🌐 Using Zyte proxy: {os.environ.get('HTTP_PROXY', '').replace(self.zyte_api_key, 'API_KEY_HIDDEN')}"
                )

                subtitle_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "nocheckcertificate": True,  # Correct yt-dlp option name for --no-check-certificate
                    "writesubtitles": True,
                    "writeautomaticsub": True,
                    "subtitleslangs": ["en"],
                    "subtitlesformat": "srt",
                    "skip_download": True,
                    "retries": 1,
                    "http_headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    },
                    # Add extractor args to focus on metadata
                    "extractor_args": {"youtube": {"skip": ["dash", "hls"]}},
                }

                with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)

                    if info:
                        subtitles = info.get("subtitles", {})
                        automatic_captions = info.get("automatic_captions", {})

                        subtitle_count = len(subtitles)
                        auto_caption_count = len(automatic_captions)

                        print(f"  🔍 Available subtitles: {list(subtitles.keys())}")
                        print(
                            f"  🔍 Available auto-captions: {list(automatic_captions.keys())}"
                        )

                        result = {
                            "success": True,
                            "video_title": info.get("title", "Unknown"),
                            "duration": info.get("duration", 0),
                            "subtitle_count": subtitle_count,
                            "auto_caption_count": auto_caption_count,
                            "available_languages": list(subtitles.keys())
                            + list(automatic_captions.keys()),
                            "attempts": attempt,
                            "proxy_used": True,
                        }

                        print(f"  ✅ Success! Title: {result['video_title']}")
                        print(
                            f"  📊 Subtitles: {subtitle_count}, Auto-captions: {auto_caption_count}"
                        )

                        # Try to download actual subtitle content using proxy
                        if subtitle_count > 0 or auto_caption_count > 0:
                            proxy_url = os.environ.get("HTTP_PROXY", "")
                            self._download_subtitle_content_with_ytdlp(
                                video_id, subtitles, automatic_captions, proxy_url
                            )

                        return result
                    else:
                        print(f"  ❌ No video info returned")

            except Exception as e:
                print(f"  ❌ Attempt {attempt} failed: {str(e)}")
                if attempt < self.max_retries:
                    time.sleep(1)

        return {
            "success": False,
            "error": "All attempts failed",
            "attempts": self.max_retries,
        }

    def _download_subtitle_content_with_ytdlp(
        self, video_id: str, subtitles: dict, automatic_captions: dict, proxy_url: str
    ):
        """Download actual subtitle content using yt-dlp with proxy"""
        print("  📥 Downloading subtitle content through yt-dlp with proxy...")

        # Configure yt-dlp for downloading subtitles with proxy
        download_opts = {
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,  # Correct yt-dlp option name for --no-check-certificate
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "subtitlesformat": "srt",
            "skip_download": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
        }

        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            with yt_dlp.YoutubeDL(download_opts) as ydl:
                # This will download subtitles to files
                ydl.download([video_url])

                # Look for downloaded subtitle files
                import glob

                subtitle_files = glob.glob(f"*{video_id}*.srt")

                if subtitle_files:
                    print(f"    ✅ Downloaded {len(subtitle_files)} subtitle files:")
                    for file in subtitle_files:
                        print(f"      📄 {file}")

                        # Show sample content
                        try:
                            with open(file, "r", encoding="utf-8") as f:
                                content = f.read()
                                lines = content.split("\n")[:5]
                                print("    📝 Sample content:")
                                for line in lines:
                                    if line.strip():
                                        print(f"      {line[:80]}...")
                                        break
                        except Exception as e:
                            print(f"    ⚠️  Could not read sample content: {e}")
                else:
                    print("    ⚠️  No subtitle files found after download")

        except Exception as e:
            print(f"    ❌ Failed to download subtitles with yt-dlp: {str(e)}")

    def _download_subtitle_content(
        self, video_id: str, subtitles: dict, automatic_captions: dict
    ):
        """Download actual subtitle content using custom proxy handler (legacy method)"""
        print("  📥 Downloading subtitle content through custom proxy...")

        # Try manual subtitles first
        for lang, subs in subtitles.items():
            if subs and len(subs) > 0:
                subtitle_url = subs[0].get("url")
                if subtitle_url:
                    try:
                        print(f"    🌐 Downloading {lang} subtitles...")
                        subtitle_content = self.zyte_proxy.make_proxy_request(
                            subtitle_url
                        )

                        # Save subtitle content to file
                        filename = f"subtitles_proxy_{video_id}_{lang}.srt"
                        with open(filename, "wb") as f:
                            f.write(subtitle_content)

                        print(
                            f"    ✅ Saved {lang} subtitles to {filename} ({len(subtitle_content)} bytes)"
                        )

                        # Show sample content
                        try:
                            content_text = subtitle_content.decode(
                                "utf-8", errors="ignore"
                            )
                            lines = content_text.split("\n")[:5]
                            print("    📝 Sample content:")
                            for line in lines:
                                if line.strip():
                                    print(f"      {line[:80]}...")
                                    break
                        except:
                            pass

                        return  # Success, exit early

                    except Exception as e:
                        print(f"    ❌ Failed to download {lang} subtitles: {str(e)}")

        # Try automatic captions if manual subtitles failed
        for lang, captions in automatic_captions.items():
            if captions and len(captions) > 0:
                caption_url = captions[0].get("url")
                if caption_url:
                    try:
                        print(f"    🌐 Downloading {lang} auto-captions...")
                        caption_content = self.zyte_proxy.make_proxy_request(
                            caption_url
                        )

                        # Save caption content to file
                        filename = f"captions_proxy_{video_id}_{lang}.srt"
                        with open(filename, "wb") as f:
                            f.write(caption_content)

                        print(
                            f"    ✅ Saved {lang} auto-captions to {filename} ({len(caption_content)} bytes)"
                        )

                        # Show sample content
                        try:
                            content_text = caption_content.decode(
                                "utf-8", errors="ignore"
                            )
                            lines = content_text.split("\n")[:5]
                            print("    📝 Sample content:")
                            for line in lines:
                                if line.strip():
                                    print(f"      {line[:80]}...")
                                    break
                        except:
                            pass

                        return  # Success, exit early

                    except Exception as e:
                        print(
                            f"    ❌ Failed to download {lang} auto-captions: {str(e)}"
                        )

    def run_tests(self) -> Dict[str, Any]:
        """Run tests for all videos"""
        print("🧪 Starting yt-dlp Proxy Tests")
        print("=" * 60)

        all_results = {}

        for video_id in self.test_videos:
            print(f"\n📹 Testing Video ID: {video_id}")
            print("-" * 40)

            video_results = self.download_subtitles_with_proxy(video_id)
            all_results[video_id] = video_results

        self.results = all_results
        return all_results

    def print_summary(self):
        """Print a comprehensive summary of all test results"""
        print("\n" + "=" * 80)
        print("📊 YT-DLP PROXY TEST SUMMARY")
        print("=" * 80)

        total_tests = len(self.results)
        successful_tests = 0

        for video_id, result in self.results.items():
            print(f"\n📹 Video ID: {video_id}")
            print("-" * 50)

            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            attempts = result.get("attempts", 0)

            print(f"  yt-dlp with proxy    {status} (attempts: {attempts})")

            if result.get("success", False):
                successful_tests += 1
                print(f"    📺 Title: {result.get('video_title', 'Unknown')}")
                print(
                    f"    📊 Subtitles: {result.get('subtitle_count', 0)}, Auto-captions: {result.get('auto_caption_count', 0)}"
                )
                print(
                    f"    🌐 Languages: {', '.join(result.get('available_languages', []))}"
                )
            else:
                error = result.get("error", "Unknown error")
                print(f"    ❌ Error: {error}")

        print("\n" + "=" * 80)
        print("📈 OVERALL STATISTICS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(
            f"Success Rate: {(successful_tests/total_tests*100):.1f}%"
            if total_tests > 0
            else "N/A"
        )

        return successful_tests == total_tests


def main():
    """Main function"""
    print("🚀 yt-dlp with Zyte Proxy Test Suite")
    print("Testing subtitle downloading with yt-dlp configured to use Zyte proxy")
    print("Videos: 1GpGqwXExYE, 9uY6N2Bl0pU")
    print("Retries: 2 per video")
    print("Proxy: Zyte (api.zyte.com:8011)")

    # Get Zyte API key from environment variable or command line
    zyte_api_key = os.getenv("ZYTE_API_KEY")
    if not zyte_api_key and len(sys.argv) > 1:
        zyte_api_key = sys.argv[1]

    if not zyte_api_key:
        print("❌ No Zyte API key provided!")
        print("   Set ZYTE_API_KEY environment variable or pass as first argument")
        print("   Example: python test_ytdlp_proxy.py YOUR_API_KEY")
        sys.exit(1)

    print("🌐 Zyte proxy API key provided - proxy will be used")

    tester = YtDlpProxyTester(zyte_api_key)

    try:
        # Test proxy connection first
        print("\n🔍 Testing proxy connection...")
        proxy_working = tester.test_proxy_connection()
        if not proxy_working:
            print("❌ Proxy test failed, cannot continue")
            sys.exit(1)

        # Run all tests
        results = tester.run_tests()

        # Print summary
        all_passed = tester.print_summary()

        # Exit with appropriate code
        if all_passed:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n💥 Some tests failed!")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
