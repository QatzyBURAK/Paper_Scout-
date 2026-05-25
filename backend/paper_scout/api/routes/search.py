from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from paper_scout.api.dependencies import get_search_service
from paper_scout.models import Paper
from paper_scout.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/keyword", response_model=list[Paper])
async def keyword(
    q: str = Query(min_length=1),
    limit: int = Query(100, ge=1, le=500),
    svc: SearchService = Depends(get_search_service),
) -> list[Paper]:
    return svc.keyword(q, limit)


@router.get("/semantic", response_model=list[Paper])
async def semantic(
    q: str = Query(min_length=1),
    limit: int = Query(100, ge=1, le=500),
    svc: SearchService = Depends(get_search_service),
) -> list[Paper]:
    return svc.semantic(q, limit)


@router.get("/hybrid", response_model=list[Paper])
async def hybrid(
    q: str = Query(min_length=1),
    limit: int = Query(100, ge=1, le=500),
    per_list_limit: int = Query(150, ge=1, le=1000),
    svc: SearchService = Depends(get_search_service),
) -> list[Paper]:
    return svc.hybrid(q, limit, per_list_limit)
