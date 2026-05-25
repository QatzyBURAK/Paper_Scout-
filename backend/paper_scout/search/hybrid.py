from __future__ import annotations


def _dedupe_ordered(ids: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for id_ in ids:
        if id_ not in seen:
            seen.add(id_)
            result.append(id_)
    return result


def rrf_combine(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion over multiple ranked ID lists.

    Each input list is deduplicated in order (first occurrence wins) before
    scoring, preventing artificial score inflation from repeated IDs.
    Returns (id, score) pairs sorted by score descending.
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item_id in enumerate(_dedupe_ordered(ranking), start=1):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
