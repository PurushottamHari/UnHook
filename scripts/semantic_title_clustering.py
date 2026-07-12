"""
Prototype script: group article titles by semantic similarity.

Dependencies: sentence-transformers, numpy, scikit-learn
"""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

SIMILARITY_THRESHOLD = 0.40
MODEL_NAME = "all-MiniLM-L6-v2"

ARTICLE_TITLES = [
    # Same event, different sources (should merge)
    "Federal Reserve raises interest rates by 25 basis points",
    "Fed hikes rates amid inflation concerns",
    "US central bank increases borrowing costs for third consecutive time",
    # Same topic, different angle (borderline — good for threshold tuning)
    "Inflation in the US falls to 3.2% in October",
    "Consumer prices ease but Fed remains cautious",
    # Crypto cluster
    "Bitcoin surges past $70,000 as ETF approval speculation grows",
    "Crypto markets rally on hopes of SEC approving spot Bitcoin ETF",
    "Ethereum also climbs as broader crypto market sees gains",
    # Completely unrelated solos
    "Arsenal beat Chelsea 2-1 in Premier League clash",
    "New study links ultra-processed foods to increased risk of depression",
    "NASA confirms water ice deposits found in lunar south pole craters",
    # Tech layoffs cluster
    "Google announces 12,000 job cuts as ad revenue slows",
    "Meta to lay off 10% of workforce in second round of cuts",
    "Tech sector sheds thousands of jobs amid economic uncertainty",
    # Adjacent but not the same (should NOT merge)
    "OpenAI releases GPT-5 with improved reasoning capabilities",
    "Anthropic raises $2 billion in latest funding round",
    # Solo with no match
    "Scotland introduces new rent control legislation for private landlords",
]


def greedy_cluster_by_threshold(
    similarity_matrix: np.ndarray, threshold: float
) -> list[list[int]]:
    n = similarity_matrix.shape[0]
    assigned = [False] * n
    groups: list[list[int]] = []

    for seed in range(n):
        if assigned[seed]:
            continue

        members = [
            idx
            for idx in range(n)
            if not assigned[idx] and similarity_matrix[seed, idx] >= threshold
        ]

        for idx in members:
            assigned[idx] = True

        groups.append(members)

    return groups


def format_group_output(
    group_number: int,
    member_indices: list[int],
    titles: list[str],
    similarity_matrix: np.ndarray,
) -> str:
    is_merge = len(member_indices) >= 2
    label = "MERGE" if is_merge else "SOLO"
    lines = [
        f"Group {group_number} [{label}] ({len(member_indices)} title(s))",
        "-" * 60,
    ]

    for idx in member_indices:
        lines.append(f"  • {titles[idx]}")

    if is_merge:
        lines.append("")
        lines.append("  Pairwise similarities:")
        for i, idx_a in enumerate(member_indices):
            for idx_b in member_indices[i + 1 :]:
                score = similarity_matrix[idx_a, idx_b]
                lines.append(f"    [{idx_a}] ↔ [{idx_b}]: {score:.3f}")

    return "\n".join(lines)


def main() -> None:
    print(f"Model: {MODEL_NAME}")
    print(f"Similarity threshold: {SIMILARITY_THRESHOLD}")
    print(f"Titles: {len(ARTICLE_TITLES)}\n")

    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(ARTICLE_TITLES, show_progress_bar=False)
    similarity_matrix = cosine_similarity(embeddings)

    groups = greedy_cluster_by_threshold(similarity_matrix, SIMILARITY_THRESHOLD)

    merge_count = sum(1 for group in groups if len(group) >= 2)
    solo_count = len(groups) - merge_count

    print(f"Found {len(groups)} groups ({merge_count} MERGE, {solo_count} SOLO)\n")
    print("=" * 60)

    for group_number, member_indices in enumerate(groups, start=1):
        print(
            format_group_output(
                group_number,
                member_indices,
                ARTICLE_TITLES,
                similarity_matrix,
            )
        )
        print("=" * 60)


if __name__ == "__main__":
    main()
