from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from paper_scout.models import Paper


class HealthResponse(BaseModel):
    status: str


class PaperListResponse(BaseModel):
    items: list[Paper]
    total: int
    limit: int
    offset: int


class IngestRequest(BaseModel):
    query: str = Field(min_length=1)
    limit_per_source: int = Field(default=25, ge=1, le=50)
    period: Literal["week", "month"] | None = None
    sources: list[Literal["arxiv", "semantic_scholar"]] | None = None


class IngestResponse(BaseModel):
    fetched: int
    saved: int
    merged: int
