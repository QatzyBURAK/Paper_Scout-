from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from paper_scout.api.dependencies import get_paper_service
from paper_scout.api.schemas import PaperListResponse
from paper_scout.models import Paper
from paper_scout.services.paper_service import PaperService

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("", response_model=PaperListResponse)
async def list_papers(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    svc: PaperService = Depends(get_paper_service),
) -> PaperListResponse:
    return PaperListResponse(
        items=svc.list_paginated(limit, offset),
        total=svc.count(),
        limit=limit,
        offset=offset,
    )


@router.get("/{external_id}", response_model=Paper)
async def get_paper(
    external_id: str,
    svc: PaperService = Depends(get_paper_service),
) -> Paper:
    paper = svc.get(external_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper
