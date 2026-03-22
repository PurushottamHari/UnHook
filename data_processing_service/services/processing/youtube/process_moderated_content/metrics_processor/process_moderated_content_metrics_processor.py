"""
Metrics processor for process moderated content service.
"""

from typing import Dict, List

from commons.metrics_processor.base_metrics_processor import BaseMetricsProcessor


class ProcessModeratedContentMetricsProcessor(BaseMetricsProcessor):
    """
    Metrics processor for process moderated content service.

    Tracks:
    - Total content considered
    - Content successfully processed
    - Processing failures
    - Subtitle language details:
        - Which languages were successfully downloaded
        - Which languages failed to download
        - Whether downloaded language matches video language
    - Subtitle download statistics:
        - Success rates for each subtitle file type
        - Retry statistics for subtitle downloads
        - Download attempts per subtitle type and language
    """

    def __init__(self, pipeline_id: str):
        """
        Initialize the process moderated content metrics processor.

        Args:
            pipeline_id: Unique identifier for the pipeline run
        """
        initial_data = {
            "total_considered": 0,
            "successfully_processed": 0,
            "processing_failures": 0,
            "content_processed": [],
            "failure_details": {},  # content_id -> failure_reason
            "subtitle_metrics": {
                "languages_downloaded": {},  # content_id -> [languages]
                "languages_failed": {},  # content_id -> [languages]
                "language_matches_video": {},  # content_id -> bool
                "video_languages": {},  # content_id -> video_language
                "subtitle_types_used": {},  # content_id -> [automatic/manual]
                "download_attempts": {},  # subtitle_key -> {attempts: int, successes: int, failures: int}
                "retry_statistics": {},  # subtitle_key -> {total_retries: int, successful_after_retries: int}
            },
        }

        super().__init__(
            service_name="process_moderated_content_service",
            pipeline_id=pipeline_id,
            data_structure=initial_data,
        )

    def record_content_considered(self, count: int = 1) -> None:
        """
        Record content that was considered for processing.

        Args:
            count: Number of content items considered
        """
        self.data["total_considered"] += count

    def record_successful_processing(self, content_id: str) -> None:
        """
        Record successful content processing.

        Args:
            content_id: ID of the content that was successfully processed
        """
        self.data["successfully_processed"] += 1
        if content_id not in self.data["content_processed"]:
            self.data["content_processed"].append(content_id)

    def record_processing_failure(self, content_id: str, reason: str) -> None:
        """
        Record processing failure.

        Args:
            content_id: ID of the content that failed processing
            reason: Reason for the failure
        """
        self.data["processing_failures"] += 1
        self.data["failure_details"][content_id] = reason
        if content_id not in self.data["content_processed"]:
            self.data["content_processed"].append(content_id)

    def record_subtitle_language_downloaded(
        self, content_id: str, language: str, subtitle_type: str
    ) -> None:
        """
        Record that a subtitle language was successfully downloaded.

        Args:
            content_id: ID of the content
            language: Language code (e.g., 'en', 'hi')
            subtitle_type: Type of subtitle ('automatic' or 'manual')
        """
        if content_id not in self.data["subtitle_metrics"]["languages_downloaded"]:
            self.data["subtitle_metrics"]["languages_downloaded"][content_id] = []

        if (
            language
            not in self.data["subtitle_metrics"]["languages_downloaded"][content_id]
        ):
            self.data["subtitle_metrics"]["languages_downloaded"][content_id].append(
                language
            )

        # Record subtitle type used
        if content_id not in self.data["subtitle_metrics"]["subtitle_types_used"]:
            self.data["subtitle_metrics"]["subtitle_types_used"][content_id] = []

        if (
            subtitle_type
            not in self.data["subtitle_metrics"]["subtitle_types_used"][content_id]
        ):
            self.data["subtitle_metrics"]["subtitle_types_used"][content_id].append(
                subtitle_type
            )

    def record_subtitle_language_failed(self, content_id: str, language: str) -> None:
        """
        Record that a subtitle language failed to download.

        Args:
            content_id: ID of the content
            language: Language code (e.g., 'en', 'hi')
        """
        if content_id not in self.data["subtitle_metrics"]["languages_failed"]:
            self.data["subtitle_metrics"]["languages_failed"][content_id] = []

        if (
            language
            not in self.data["subtitle_metrics"]["languages_failed"][content_id]
        ):
            self.data["subtitle_metrics"]["languages_failed"][content_id].append(
                language
            )

    def record_video_language(self, content_id: str, video_language: str) -> None:
        """
        Record the language of the video.

        Args:
            content_id: ID of the content
            video_language: Language of the video
        """
        self.data["subtitle_metrics"]["video_languages"][content_id] = video_language

    def record_language_match_result(self, content_id: str, matches: bool) -> None:
        """
        Record whether the downloaded subtitle language matches the video language.

        Args:
            content_id: ID of the content
            matches: True if languages match, False otherwise
        """
        self.data["subtitle_metrics"]["language_matches_video"][content_id] = matches

    def record_subtitle_download_attempt(
        self,
        content_id: str,
        language: str,
        subtitle_type: str,
        extension: str,
        success: bool,
        retry_count: int = 0,
    ) -> None:
        """
        Record a subtitle download attempt with success/failure and retry information.

        Args:
            content_id: ID of the content
            language: Language code (e.g., 'en', 'hi')
            subtitle_type: Type of subtitle ('automatic' or 'manual')
            extension: File extension (e.g., 'srt', 'vtt', 'json3')
            success: Whether the download was successful
            retry_count: Number of retries before this attempt
        """
        # Create a unique key for this subtitle file
        subtitle_key = f"{content_id}_{language}_{subtitle_type}_{extension}"

        # Initialize download attempts tracking
        if subtitle_key not in self.data["subtitle_metrics"]["download_attempts"]:
            self.data["subtitle_metrics"]["download_attempts"][subtitle_key] = {
                "attempts": 0,
                "successes": 0,
                "failures": 0,
                "content_id": content_id,
                "language": language,
                "subtitle_type": subtitle_type,
                "extension": extension,
            }

        # Update attempt counts
        self.data["subtitle_metrics"]["download_attempts"][subtitle_key][
            "attempts"
        ] += 1
        if success:
            self.data["subtitle_metrics"]["download_attempts"][subtitle_key][
                "successes"
            ] += 1
        else:
            self.data["subtitle_metrics"]["download_attempts"][subtitle_key][
                "failures"
            ] += 1

        # Track retry statistics
        if retry_count > 0:
            if subtitle_key not in self.data["subtitle_metrics"]["retry_statistics"]:
                self.data["subtitle_metrics"]["retry_statistics"][subtitle_key] = {
                    "total_retries": 0,
                    "successful_after_retries": 0,
                    "content_id": content_id,
                    "language": language,
                    "subtitle_type": subtitle_type,
                    "extension": extension,
                }

            self.data["subtitle_metrics"]["retry_statistics"][subtitle_key][
                "total_retries"
            ] += retry_count
            if success:
                self.data["subtitle_metrics"]["retry_statistics"][subtitle_key][
                    "successful_after_retries"
                ] += 1

    def get_total_considered(self) -> int:
        """
        Get the total number of content items considered.

        Returns:
            Total number of content items considered
        """
        return self.data["total_considered"]

    def get_successfully_processed_count(self) -> int:
        """
        Get the number of successfully processed items.

        Returns:
            Number of successfully processed items
        """
        return self.data["successfully_processed"]

    def get_processing_failures_count(self) -> int:
        """
        Get the number of processing failures.

        Returns:
            Number of processing failures
        """
        return self.data["processing_failures"]

    def get_content_processed(self) -> List[str]:
        """
        Get the list of content IDs that were processed.

        Returns:
            List of content IDs that were processed
        """
        return self.data["content_processed"]

    def get_failure_details(self) -> Dict[str, str]:
        """
        Get detailed failure information.

        Returns:
            Dictionary mapping content IDs to failure reasons
        """
        return self.data["failure_details"]

    def get_subtitle_metrics(self) -> Dict:
        """
        Get detailed subtitle metrics.

        Returns:
            Dictionary containing all subtitle-related metrics
        """
        return self.data["subtitle_metrics"]

    def get_languages_downloaded(self) -> Dict[str, List[str]]:
        """
        Get languages downloaded for each content.

        Returns:
            Dictionary mapping content IDs to list of downloaded languages
        """
        return self.data["subtitle_metrics"]["languages_downloaded"]

    def get_languages_failed(self) -> Dict[str, List[str]]:
        """
        Get languages that failed to download for each content.

        Returns:
            Dictionary mapping content IDs to list of failed languages
        """
        return self.data["subtitle_metrics"]["languages_failed"]

    def get_language_match_results(self) -> Dict[str, bool]:
        """
        Get language match results for each content.

        Returns:
            Dictionary mapping content IDs to boolean indicating if languages match
        """
        return self.data["subtitle_metrics"]["language_matches_video"]

    def get_download_attempts(self) -> Dict[str, Dict]:
        """
        Get download attempt statistics for each subtitle file.

        Returns:
            Dictionary mapping subtitle keys to download attempt statistics
        """
        return self.data["subtitle_metrics"]["download_attempts"]

    def get_retry_statistics(self) -> Dict[str, Dict]:
        """
        Get retry statistics for subtitle downloads.

        Returns:
            Dictionary mapping subtitle keys to retry statistics
        """
        return self.data["subtitle_metrics"]["retry_statistics"]

    def get_download_success_rates(self) -> Dict[str, float]:
        """
        Get download success rates for each subtitle file type.

        Returns:
            Dictionary mapping subtitle keys to success rates (0.0 to 1.0)
        """
        success_rates = {}
        for subtitle_key, stats in self.data["subtitle_metrics"][
            "download_attempts"
        ].items():
            if stats["attempts"] > 0:
                success_rate = stats["successes"] / stats["attempts"]
                success_rates[subtitle_key] = success_rate
            else:
                success_rates[subtitle_key] = 0.0
        return success_rates

    def get_aggregated_success_rates(self) -> Dict[str, Dict]:
        """
        Get aggregated success rates by subtitle type, language, and extension.

        Returns:
            Dictionary with aggregated success rates by category
        """
        aggregated = {
            "by_subtitle_type": {
                "automatic": {"attempts": 0, "successes": 0},
                "manual": {"attempts": 0, "successes": 0},
            },
            "by_language": {
                "en": {"attempts": 0, "successes": 0},
                "hi": {"attempts": 0, "successes": 0},
            },
            "by_extension": {
                "srt": {"attempts": 0, "successes": 0},
                "vtt": {"attempts": 0, "successes": 0},
                "json3": {"attempts": 0, "successes": 0},
            },
        }

        for subtitle_key, stats in self.data["subtitle_metrics"][
            "download_attempts"
        ].items():
            # Aggregate by subtitle type
            subtitle_type = stats["subtitle_type"]
            aggregated["by_subtitle_type"][subtitle_type]["attempts"] += stats[
                "attempts"
            ]
            aggregated["by_subtitle_type"][subtitle_type]["successes"] += stats[
                "successes"
            ]

            # Aggregate by language
            language = stats["language"]
            if language in aggregated["by_language"]:
                aggregated["by_language"][language]["attempts"] += stats["attempts"]
                aggregated["by_language"][language]["successes"] += stats["successes"]

            # Aggregate by extension
            extension = stats["extension"]
            if extension in aggregated["by_extension"]:
                aggregated["by_extension"][extension]["attempts"] += stats["attempts"]
                aggregated["by_extension"][extension]["successes"] += stats["successes"]

        # Calculate success rates
        for category in aggregated.values():
            for key, stats in category.items():
                if stats["attempts"] > 0:
                    stats["success_rate"] = stats["successes"] / stats["attempts"]
                else:
                    stats["success_rate"] = 0.0

        return aggregated

    def print_enhanced_metrics_summary(self) -> None:
        """Print enhanced metrics summary including subtitle details."""
        print(
            f"✅ Process moderated content completed. Considered: {self.get_total_considered()}, "
            f"Successfully processed: {self.get_successfully_processed_count()}, "
            f"Failures: {self.get_processing_failures_count()}"
        )

        # Print subtitle-specific metrics
        subtitle_metrics = self.data["subtitle_metrics"]

        # Language download statistics
        languages_downloaded = subtitle_metrics["languages_downloaded"]
        languages_failed = subtitle_metrics["languages_failed"]
        language_matches = subtitle_metrics["language_matches_video"]

        total_videos_with_subtitles = len(languages_downloaded)
        total_languages_downloaded = sum(
            len(langs) for langs in languages_downloaded.values()
        )
        total_languages_failed = sum(len(langs) for langs in languages_failed.values())

        if total_videos_with_subtitles > 0:
            print(f"📊 Subtitle Metrics:")
            print(f"   Videos with subtitles downloaded: {total_videos_with_subtitles}")
            print(f"   Total languages downloaded: {total_languages_downloaded}")
            print(f"   Total languages failed: {total_languages_failed}")

            # Language match statistics
            if language_matches:
                matches_count = sum(
                    1 for matches in language_matches.values() if matches
                )
                total_with_language_info = len(language_matches)
                match_percentage = (
                    (matches_count / total_with_language_info * 100)
                    if total_with_language_info > 0
                    else 0
                )
                print(
                    f"   Language matches video: {matches_count}/{total_with_language_info} ({match_percentage:.1f}%)"
                )

            # Subtitle type statistics
            subtitle_types = subtitle_metrics["subtitle_types_used"]
            automatic_count = sum(
                1 for types in subtitle_types.values() if "automatic" in types
            )
            manual_count = sum(
                1 for types in subtitle_types.values() if "manual" in types
            )
            print(f"   Automatic subtitles used: {automatic_count}")
            print(f"   Manual subtitles used: {manual_count}")

            # Download success rate statistics
            download_attempts = subtitle_metrics["download_attempts"]
            if download_attempts:
                print(f"📈 Download Success Rates:")

                # Get aggregated success rates
                aggregated_rates = self.get_aggregated_success_rates()

                # By subtitle type
                print(f"   By Subtitle Type:")
                for subtitle_type, stats in aggregated_rates[
                    "by_subtitle_type"
                ].items():
                    if stats["attempts"] > 0:
                        success_rate = stats["success_rate"] * 100
                        print(
                            f"     {subtitle_type.capitalize()}: {stats['successes']}/{stats['attempts']} ({success_rate:.1f}%)"
                        )

                # By language
                print(f"   By Language:")
                for language, stats in aggregated_rates["by_language"].items():
                    if stats["attempts"] > 0:
                        success_rate = stats["success_rate"] * 100
                        print(
                            f"     {language.upper()}: {stats['successes']}/{stats['attempts']} ({success_rate:.1f}%)"
                        )

                # By extension
                print(f"   By Extension:")
                for extension, stats in aggregated_rates["by_extension"].items():
                    if stats["attempts"] > 0:
                        success_rate = stats["success_rate"] * 100
                        print(
                            f"     {extension.upper()}: {stats['successes']}/{stats['attempts']} ({success_rate:.1f}%)"
                        )

                # Overall success rate
                total_attempts = sum(
                    stats["attempts"] for stats in download_attempts.values()
                )
                total_successes = sum(
                    stats["successes"] for stats in download_attempts.values()
                )
                if total_attempts > 0:
                    overall_success_rate = (total_successes / total_attempts) * 100
                    print(
                        f"   Overall: {total_successes}/{total_attempts} ({overall_success_rate:.1f}%)"
                    )

            # Retry statistics
            retry_stats = subtitle_metrics["retry_statistics"]
            if retry_stats:
                print(f"🔄 Retry Statistics:")
                total_retries = sum(
                    stats["total_retries"] for stats in retry_stats.values()
                )
                successful_after_retries = sum(
                    stats["successful_after_retries"] for stats in retry_stats.values()
                )
                print(f"   Total retries: {total_retries}")
                print(f"   Successful after retries: {successful_after_retries}")
                if total_retries > 0:
                    retry_success_rate = (
                        successful_after_retries / total_retries
                    ) * 100
                    print(f"   Retry success rate: {retry_success_rate:.1f}%")

            # Detailed breakdown by content
            if languages_downloaded:
                print(f"   Detailed breakdown:")
                for content_id, langs in languages_downloaded.items():
                    video_lang = subtitle_metrics["video_languages"].get(
                        content_id, "Unknown"
                    )
                    matches = language_matches.get(content_id, None)
                    match_status = (
                        "✅" if matches else "❌" if matches is False else "❓"
                    )
                    failed_langs = languages_failed.get(content_id, [])
                    failed_str = (
                        f" (Failed: {', '.join(failed_langs)})" if failed_langs else ""
                    )
                    print(
                        f"     {content_id}: {', '.join(langs)} (Video: {video_lang}) {match_status}{failed_str}"
                    )

                    # Show download attempts for this content
                    content_attempts = {
                        k: v
                        for k, v in download_attempts.items()
                        if v["content_id"] == content_id
                    }
                    if content_attempts:
                        print(f"       Download attempts:")
                        for subtitle_key, stats in content_attempts.items():
                            success_rate = (
                                (stats["successes"] / stats["attempts"] * 100)
                                if stats["attempts"] > 0
                                else 0
                            )
                            print(
                                f"         {stats['language']}_{stats['subtitle_type']}_{stats['extension']}: {stats['successes']}/{stats['attempts']} ({success_rate:.1f}%)"
                            )
