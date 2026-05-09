from typing import List, Optional

from ..models import NewspaperArticleCandidate, NewspaperV2


def aggregate_newspapers(
    newspapers: List[NewspaperV2], candidates: List[NewspaperArticleCandidate]
) -> NewspaperV2:
    """
    Aggregates multiple NewspaperV2 instances into a single one.

    - Uses the latest newspaper as the primary metadata source (ID, status).
    - Sums up the reading_time_in_seconds.
    - Merges status_details.
    - Note: The candidates are expected to be already filtered (e.g., status=USED).
    """
    if not newspapers:
        raise ValueError("Cannot aggregate empty newspaper list")

    # Sort newspapers by created_at descending to pick the most recent as primary
    sorted_newspapers = sorted(newspapers, key=lambda n: n.created_at)
    main_newspaper = sorted_newspapers[-1]

    # Aggregate reading time
    main_newspaper.reading_time_in_seconds = sum(
        n.reading_time_in_seconds for n in newspapers
    )

    # Merge status details (unique by content/timestamp if possible, or just concat)
    merged_details = []
    for n in newspapers:
        if n.status_details:
            merged_details.extend(n.status_details)

    # Sort merged details by created_at if they have it
    try:
        merged_details.sort(key=lambda d: getattr(d, "created_at", 0))
    except (AttributeError, TypeError):
        pass

    main_newspaper.status_details = merged_details

    return main_newspaper
