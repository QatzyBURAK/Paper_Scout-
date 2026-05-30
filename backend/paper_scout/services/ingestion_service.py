from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

from paper_scout.db.repository import list_all_papers
from paper_scout.fetchers.base import Fetcher
from paper_scout.models import Paper
from paper_scout.services.dedup import is_duplicate, merge, normalize_title
from paper_scout.services.paper_service import PaperService, SessionFactory

logger = logging.getLogger(__name__)


def _since_date(period: Literal["week", "month"] | None) -> date | None:
    if period == "week":
        return date.today() - timedelta(days=7)
    if period == "month":
        return date.today() - timedelta(days=30)
    return None


@dataclass(frozen=True)
class IngestionReport:
    fetched: int
    saved: int
    merged: int


class IngestionService:
    """Orchestrates fetching, deduplication, and persistence."""

    def __init__(
        self,
        fetchers: list[Fetcher],
        paper_service: PaperService,
        session_factory: SessionFactory,
    ) -> None:
        self._fetchers = fetchers
        self._paper_service = paper_service
        self._factory = session_factory

    def ingest(
        self,
        query: str,
        limit_per_source: int = 25,
        period: Literal["week", "month"] | None = None,
        sources: Sequence[str] | None = None,
    ) -> IngestionReport:
        since = _since_date(period)
        # 1) Fetch from selected sources
        all_incoming: list[Paper] = []
        errors: list[Exception] = []
        fetched_any = False
        active_fetchers_count = 0

        for f in self._fetchers:
            if sources is not None and f.source_name not in sources:
                continue
            active_fetchers_count += 1
            try:
                papers = f.fetch(query, limit_per_source, since)
                all_incoming.extend(papers)
                fetched_any = True
            except Exception as exc:
                logger.warning("Fetcher %s failed: %s", f.source_name, exc)
                errors.append(exc)

        # If all active fetchers failed, propagate the first error to the caller (no silent swallowing)
        if active_fetchers_count > 0 and not fetched_any and errors:
            raise errors[0]

        # 2) Load existing papers → in-memory dedup index
        with self._factory() as session:
            existing = list_all_papers(session)
        idx: dict[str, list[Paper]] = {}
        for p in existing:
            idx.setdefault(normalize_title(p.title), []).append(p)

        # 3) Process incoming papers
        saved_papers: list[Paper] = []
        merged_papers: list[Paper] = []

        for incoming in all_incoming:
            norm = normalize_title(incoming.title)
            candidates = idx.get(norm, [])

            match: Paper | None = None
            for candidate in candidates:
                if is_duplicate(candidate, incoming):
                    match = candidate
                    break

            if match is not None:
                merged = merge(match, incoming)
                # Update idx so subsequent duplicates see the latest merged version
                idx[norm] = [merged if p is match else p for p in idx[norm]]
                merged_papers.append(merged)
            else:
                saved_papers.append(incoming)
                idx.setdefault(norm, []).append(incoming)

        # 4) Batch write — deduplicate by external_id so a paper that starts in
        #    saved_papers and later gets merged doesn't produce a Chroma duplicate.
        #    merged_papers takes precedence (iterated last, overwrites same key).
        final: dict[str, Paper] = {p.external_id: p for p in [*saved_papers, *merged_papers]}
        self._paper_service.save_many(list(final.values()))

        return IngestionReport(
            fetched=len(all_incoming),
            saved=len(saved_papers),
            merged=len(merged_papers),
        )
