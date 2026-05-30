from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
import httpx

from paper_scout.api.dependencies import get_ingestion_service
from paper_scout.api.schemas import IngestRequest, IngestResponse
from paper_scout.services.ingestion_service import IngestionService

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    body: IngestRequest,
    svc: IngestionService = Depends(get_ingestion_service),
) -> IngestResponse:
    try:
        report = svc.ingest(body.query, body.limit_per_source, body.period, body.sources)
        return IngestResponse(fetched=report.fetched, saved=report.saved, merged=report.merged)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="Dış akademik servisler (arXiv/Semantic Scholar) çok fazla istek aldıklarını bildirdi. Lütfen 1-2 dakika sonra tekrar deneyiniz."
            )
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Dış akademik servis sorgusu başarısız oldu: {exc.response.reason_phrase} (Hata {exc.response.status_code})"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Dış akademik servislere bağlanırken zaman aşımı (timeout) oluştu. Lütfen tekrar deneyiniz."
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Dış akademik servislere bağlanılamadı: {str(exc)}"
        )
