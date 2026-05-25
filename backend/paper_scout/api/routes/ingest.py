from __future__ import annotations

from fastapi import APIRouter, Depends

from paper_scout.api.dependencies import get_ingestion_service
from paper_scout.api.schemas import IngestRequest, IngestResponse
from paper_scout.services.ingestion_service import IngestionService

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    body: IngestRequest,
    svc: IngestionService = Depends(get_ingestion_service),
) -> IngestResponse:
    report = svc.ingest(body.query, body.limit_per_source, body.period, body.sources)
    return IngestResponse(fetched=report.fetched, saved=report.saved, merged=report.merged)
