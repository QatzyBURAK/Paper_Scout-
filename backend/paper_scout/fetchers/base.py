from __future__ import annotations

from datetime import date
from typing import Protocol

from paper_scout.models import Paper


class Fetcher(Protocol):
    source_name: str

    def fetch(self, query: str, limit: int, since: date | None = None) -> list[Paper]: ...
