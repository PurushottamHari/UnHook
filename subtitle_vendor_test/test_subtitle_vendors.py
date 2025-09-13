#!/usr/bin/env python3
"""
Test script for YouTube subtitle downloading with multiple vendors.
Tests yt-dlp, EasySubAPI, and youtube-transcript-api with retry logic.
"""

import json
import os
import sys
import time
import traceback
from typing import Any, Dict, List, Optional

# Import the subtitle libraries
try:
    import yt_dlp

    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("⚠️  yt-dlp not available")

try:
    from youtube_transcript_api import YouTubeTranscriptApi

    YOUTUBE_TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_API_AVAILABLE = False
    print("⚠️  youtube-transcript-api not available")

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests not available (needed for EasySubAPI)")


class SubtitleVendorTester:
    """Test class for different subtitle vendors"""

    def __init__(self):
        self.results = {}
        self.test_videos = ["1GpGqwXExYE", "9uY6N2Bl0pU"]
        self.max_retries = 2

    def test_yt_dlp(self, video_id: str) -> Dict[str, Any]:
        """Test yt-dlp subtitle downloading"""
        print(f"\n🔧 Testing yt-dlp for video: {video_id}")

        if not YT_DLP_AVAILABLE:
            return {"success": False, "error": "yt-dlp not available", "attempts": 0}

        subtitle_opts = {
            "quiet": True,
            "no_warnings": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "subtitlesformat": "srt",
            "skip_download": True,
            "retries": 1,
        }

        for attempt in range(1, self.max_retries + 1):
            print(f"  🔄 Attempt {attempt}/{self.max_retries}")
            try:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    if info:
                        # Check if subtitles are available
                        subtitles = info.get("subtitles", {})
                        automatic_captions = info.get("automatic_captions", {})

                        subtitle_count = len(subtitles)
                        auto_caption_count = len(automatic_captions)

                        result = {
                            "success": True,
                            "video_title": info.get("title", "Unknown"),
                            "duration": info.get("duration", 0),
                            "subtitle_count": subtitle_count,
                            "auto_caption_count": auto_caption_count,
                            "available_languages": list(subtitles.keys())
                            + list(automatic_captions.keys()),
                            "attempts": attempt,
                        }

                    print(f"  ✅ Success! Title: {result['video_title']}")
                    print(
                        f"  📊 Subtitles: {subtitle_count}, Auto-captions: {auto_caption_count}"
                    )

                    # Print sample subtitle data for validation
                    if subtitle_count > 0:
                        print("  📝 Sample subtitle data:")
                        for lang, subs in list(subtitles.items())[
                            :1
                        ]:  # First language only
                            if subs:
                                print(f"    Language: {lang}")
                                print(
                                    f"    Sample: {subs[0].get('ext', 'unknown')} format"
                                )
                    elif auto_caption_count > 0:
                        print("  📝 Sample auto-caption data:")
                        for lang, captions in list(automatic_captions.items())[
                            :1
                        ]:  # First language only
                            if captions:
                                print(f"    Language: {lang}")
                                print(
                                    f"    Sample: {captions[0].get('ext', 'unknown')} format"
                                )

                        return result
                    else:
                        print(f"  ❌ No video info returned")

            except Exception as e:
                print(f"  ❌ Attempt {attempt} failed: {str(e)}")
                if attempt < self.max_retries:
                    time.sleep(1)  # Brief delay before retry

        return {
            "success": False,
            "error": "All attempts failed",
            "attempts": self.max_retries,
        }

    def test_youtube_transcript_api(self, video_id: str) -> Dict[str, Any]:
        """Test youtube-transcript-api subtitle downloading"""
        print(f"\n🔧 Testing youtube-transcript-api for video: {video_id}")

        if not YOUTUBE_TRANSCRIPT_API_AVAILABLE:
            return {
                "success": False,
                "error": "youtube-transcript-api not available",
                "attempts": 0,
            }

        for attempt in range(1, self.max_retries + 1):
            print(f"  🔄 Attempt {attempt}/{self.max_retries}")
            try:
                # Create API instance and fetch transcript
                ytt_api = YouTubeTranscriptApi()
                # Try English first, then Hindi as fallback
                try:
                    fetched_transcript = ytt_api.fetch(video_id, languages=["en"])
                except:
                    # Fallback to Hindi if English not available
                    fetched_transcript = ytt_api.fetch(video_id, languages=["hi"])

                if fetched_transcript and len(fetched_transcript) > 0:
                    result = {
                        "success": True,
                        "video_id": fetched_transcript.video_id,
                        "language": fetched_transcript.language,
                        "language_code": fetched_transcript.language_code,
                        "is_generated": fetched_transcript.is_generated,
                        "snippet_count": len(fetched_transcript),
                        "first_snippet": (
                            {
                                "text": (
                                    fetched_transcript[0].text
                                    if fetched_transcript
                                    else ""
                                ),
                                "start": (
                                    fetched_transcript[0].start
                                    if fetched_transcript
                                    else 0
                                ),
                                "duration": (
                                    fetched_transcript[0].duration
                                    if fetched_transcript
                                    else 0
                                ),
                            }
                            if fetched_transcript
                            else None
                        ),
                        "attempts": attempt,
                    }

                    print(
                        f"  ✅ Success! Language: {result['language']}, Generated: {result['is_generated']}"
                    )
                    print(f"  📊 Snippets: {result['snippet_count']}")

                    # Print sample transcript data for validation
                    if result.get("first_snippet"):
                        snippet = result["first_snippet"]
                        print("  📝 Sample transcript data:")
                        print(f"    Text: {snippet['text'][:100]}...")
                        print(
                            f"    Start: {snippet['start']}s, Duration: {snippet['duration']}s"
                        )

                    return result
                else:
                    print(f"  ❌ No transcript data returned")

            except Exception as e:
                print(f"  ❌ Attempt {attempt} failed: {str(e)}")
                if attempt < self.max_retries:
                    time.sleep(1)  # Brief delay before retry

        return {
            "success": False,
            "error": "All attempts failed",
            "attempts": self.max_retries,
        }

    def test_easysub_api(self, video_id: str) -> Dict[str, Any]:
        """Test EasySubAPI subtitle downloading"""
        print(f"\n🔧 Testing EasySubAPI for video: {video_id}")

        if not REQUESTS_AVAILABLE:
            return {"success": False, "error": "requests not available", "attempts": 0}

        # EasySubAPI configuration
        api_url = "https://easysubapi.p.rapidapi.com/api/easysubapi-get-transcript"
        headers = {
            "Content-Type": "application/json",
            "x-rapidapi-host": "easysubapi.p.rapidapi.com",
            "x-rapidapi-key": "bdfcd37371mshd311774678d734ap1a30f7jsncb5982ae004c",
        }

        for attempt in range(1, self.max_retries + 1):
            print(f"  🔄 Attempt {attempt}/{self.max_retries}")
            try:
                # Make POST request to EasySubAPI
                payload = {"video_id": video_id}
                response = requests.post(
                    api_url, headers=headers, json=payload, timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    result = {
                        "success": True,
                        "status_code": response.status_code,
                        "response_data": data,
                        "attempts": attempt,
                    }
                    print(f"  ✅ Success! Status: {response.status_code}")

                    # Print sample API response for validation
                    if data:
                        print("  📝 Sample API response:")
                        if isinstance(data, dict):
                            # Show first few keys of the response
                            keys = list(data.keys())[:3]
                            print(f"    Response keys: {keys}")
                            # Show a sample value if it's a string or simple type
                            for key in keys[:1]:
                                value = data[key]
                                if isinstance(value, str):
                                    print(f"    {key}: {value[:100]}...")
                                elif isinstance(value, (int, float, bool)):
                                    print(f"    {key}: {value}")
                        else:
                            print(f"    Response type: {type(data)}")

                    return result
                else:
                    print(f"  ❌ HTTP {response.status_code}: {response.text[:200]}...")

            except requests.exceptions.RequestException as e:
                print(f"  ❌ Request failed: {str(e)}")
            except Exception as e:
                print(f"  ❌ Attempt {attempt} failed: {str(e)}")

            if attempt < self.max_retries:
                time.sleep(1)  # Brief delay before retry

        return {
            "success": False,
            "error": "All attempts failed",
            "attempts": self.max_retries,
        }

    def run_tests(self) -> Dict[str, Any]:
        """Run all tests for all videos"""
        print("🧪 Starting Subtitle Vendor Tests")
        print("=" * 60)

        all_results = {}

        for video_id in self.test_videos:
            print(f"\n📹 Testing Video ID: {video_id}")
            print("-" * 40)

            video_results = {}

            # Test yt-dlp
            video_results["yt_dlp"] = self.test_yt_dlp(video_id)

            # Test youtube-transcript-api
            video_results["youtube_transcript_api"] = self.test_youtube_transcript_api(
                video_id
            )

            # Test EasySubAPI
            video_results["easysub_api"] = self.test_easysub_api(video_id)

            all_results[video_id] = video_results

        self.results = all_results
        return all_results

    def print_summary(self):
        """Print a comprehensive summary of all test results"""
        print("\n" + "=" * 80)
        print("📊 SUBTITLE VENDOR TEST SUMMARY")
        print("=" * 80)

        total_tests = 0
        successful_tests = 0

        for video_id, video_results in self.results.items():
            print(f"\n📹 Video ID: {video_id}")
            print("-" * 50)

            for vendor, result in video_results.items():
                total_tests += 1
                status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
                attempts = result.get("attempts", 0)

                print(f"  {vendor:25} {status} (attempts: {attempts})")

                if result.get("success", False):
                    successful_tests += 1

                    # Print vendor-specific success details
                    if vendor == "yt_dlp" and "video_title" in result:
                        print(f"    📺 Title: {result['video_title']}")
                        print(
                            f"    📊 Subtitles: {result.get('subtitle_count', 0)}, Auto-captions: {result.get('auto_caption_count', 0)}"
                        )
                    elif (
                        vendor == "youtube_transcript_api" and "snippet_count" in result
                    ):
                        print(
                            f"    🌐 Language: {result.get('language', 'Unknown')} ({result.get('language_code', 'Unknown')})"
                        )
                        print(
                            f"    🤖 Generated: {result.get('is_generated', 'Unknown')}, Snippets: {result.get('snippet_count', 0)}"
                        )
                        if result.get("first_snippet"):
                            print(
                                f"    📝 First snippet: {result['first_snippet']['text'][:50]}..."
                            )
                    elif vendor == "easysub_api" and "status_code" in result:
                        print(f"    🌐 Status: {result['status_code']}")
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

        # Vendor-specific statistics
        vendor_stats = {}
        for video_results in self.results.values():
            for vendor, result in video_results.items():
                if vendor not in vendor_stats:
                    vendor_stats[vendor] = {"total": 0, "success": 0}
                vendor_stats[vendor]["total"] += 1
                if result.get("success", False):
                    vendor_stats[vendor]["success"] += 1

        print(f"\n📊 VENDOR BREAKDOWN:")
        for vendor, stats in vendor_stats.items():
            success_rate = (
                (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            )
            print(
                f"  {vendor:25} {stats['success']}/{stats['total']} ({success_rate:.1f}%)"
            )

        return successful_tests == total_tests


def main():
    """Main function"""
    print("🚀 YouTube Subtitle Vendor Test Suite")
    print("Testing: yt-dlp, youtube-transcript-api, EasySubAPI")
    print("Videos: 1GpGqwXExYE, 9uY6N2Bl0pU")
    print("Retries: 2 per vendor per video")

    tester = SubtitleVendorTester()

    try:
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
