from __future__ import annotations

from typing import cast

from fastapi import Request

from paper_scout.services.ingestion_service import IngestionService
from paper_scout.services.paper_service import PaperService
from paper_scout.services.search_service import SearchService


def get_search_service(request: Request) -> SearchService:
    return cast(SearchService, request.app.state.search_service)


def get_ingestion_service(request: Request) -> IngestionService:
    return cast(IngestionService, request.app.state.ingestion_service)


def get_paper_service(request: Request) -> PaperService:
    return cast(PaperService, request.app.state.paper_service)
