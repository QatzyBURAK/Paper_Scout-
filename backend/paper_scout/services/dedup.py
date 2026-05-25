from __future__ import annotations

import re
from datetime import date

from paper_scout.models import Paper


def normalize_title(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _last_name(author: str) -> str:
    """Extract normalized last name.

    Handles both 'Last, First' (comma format) and 'First Last' (natural order).
    Returns empty string for empty/whitespace input.
    """
    author = author.strip()
    if not author:
        return ""
    if "," in author:
        raw = author.split(",", 1)[0].strip()
    else:
        parts = author.split()
        raw = parts[-1].strip() if parts else ""
    return re.sub(r"[^a-z]", "", raw.lower())


def author_overlap(a: list[str], b: list[str]) -> int:
    a_names = {_last_name(n) for n in a}
    b_names = {_last_name(n) for n in b}
    # empty string is not a valid last name
    a_names.discard("")
    b_names.discard("")
    return len(a_names & b_names)


def is_duplicate(p1: Paper, p2: Paper) -> bool:
    return (
        normalize_title(p1.title) == normalize_title(p2.title)
        and author_overlap(list(p1.authors), list(p2.authors)) >= 1
    )


def merge(existing: Paper, incoming: Paper) -> Paper:
    """Merge two records of the same paper.

    existing's external_id / source / url / title / abstract are preserved.
    citation_count = max; authors = order-preserving union (existing-first);
    published_date = earliest non-None value.
    """
    citation = max(existing.citation_count, incoming.citation_count)

    seen: set[str] = set()
    merged_authors: list[str] = []
    for a in list(existing.authors):
        if a not in seen:
            seen.add(a)
            merged_authors.append(a)
    for a in list(incoming.authors):
        if a not in seen:
            seen.add(a)
            merged_authors.append(a)

    dates: list[date] = [
        d for d in [existing.published_date, incoming.published_date] if d is not None
    ]
    pub_date: date | None = min(dates) if dates else None

    return Paper(
        external_id=existing.external_id,
        source=existing.source,
        title=existing.title,
        abstract=existing.abstract,
        authors=merged_authors,
        published_date=pub_date,
        citation_count=citation,
        url=existing.url,
    )
