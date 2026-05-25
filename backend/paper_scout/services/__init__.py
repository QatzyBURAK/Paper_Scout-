from __future__ import annotations

from paper_scout.services.dedup import author_overlap, is_duplicate, merge, normalize_title
from paper_scout.services.ingestion_service import IngestionReport, IngestionService
from paper_scout.services.paper_service import PaperService, SessionFactory
from paper_scout.services.search_service import SearchService

__all__ = [
    "IngestionReport",
    "IngestionService",
    "PaperService",
    "SearchService",
    "SessionFactory",
    "author_overlap",
    "is_duplicate",
    "merge",
    "normalize_title",
]
