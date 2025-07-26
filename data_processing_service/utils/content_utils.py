import re
from typing import Optional


def calculate_reading_time(article: str, words_per_minute: Optional[int] = None) -> int:
    """
    Calculate the reading time for an article in seconds.

    Args:
        article (str): The article text to calculate reading time for
        words_per_minute (Optional[int]): Reading speed in words per minute.
                                        Defaults to 200 WPM (average adult reading speed)

    Returns:
        int: Reading time in seconds

    Example:
        >>> calculate_reading_time("This is a short article with some words.")
        3
        >>> calculate_reading_time("Long article...", words_per_minute=150)
        20
    """
    if not article or not article.strip():
        return 0

    # Default to average adult reading speed if not provided
    if words_per_minute is None:
        words_per_minute = 200

    # Count words by splitting on whitespace and filtering out empty strings
    words = [word for word in re.split(r"\s+", article.strip()) if word]
    word_count = len(words)

    # Calculate reading time in minutes, then convert to seconds
    reading_time_minutes = word_count / words_per_minute
    reading_time_seconds = int(reading_time_minutes * 60)

    # Ensure at least 1 second for very short content
    return max(1, reading_time_seconds)
