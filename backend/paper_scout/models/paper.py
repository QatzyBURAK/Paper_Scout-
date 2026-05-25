from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PaperSource = Literal["arxiv", "semantic_scholar"]


class Paper(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    external_id: str = Field(min_length=1)
    source: PaperSource
    title: str = Field(min_length=1)
    abstract: str
    authors: list[str] = Field(default_factory=list)
    published_date: date | None = None
    citation_count: int = Field(default=0, ge=0)
    url: str = Field(min_length=1)
