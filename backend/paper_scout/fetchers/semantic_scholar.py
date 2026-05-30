from __future__ import annotations

import logging
from datetime import date
from typing import Any

import httpx
from pydantic import ValidationError

from paper_scout.models import Paper

logger = logging.getLogger(__name__)

_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/search"
_FIELDS = "paperId,title,abstract,authors,publicationDate,citationCount,url"
_TIMEOUT = 7.0
_USER_AGENT = "paper-scout/0.1"


def _make_client() -> httpx.Client:
    return httpx.Client(timeout=_TIMEOUT, headers={"User-Agent": _USER_AGENT})


class SemanticScholarFetcher:
    source_name: str = "semantic_scholar"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client if client is not None else _make_client()

    def close(self) -> None:
        self._client.close()

    def fetch(self, query: str, limit: int, since: date | None = None) -> list[Paper]:
        if not query:
            raise ValueError("query must not be empty")
        if limit <= 0:
            raise ValueError(f"limit must be positive, got {limit}")

        params: dict[str, str | int] = {"query": query, "limit": limit, "fields": _FIELDS}
        if since is not None:
            params["publicationDateOrYear"] = f"{since.isoformat()}:{date.today().isoformat()}"

        response = self._client.get(_ENDPOINT, params=params)
        response.raise_for_status()

        payload: dict[str, Any] = response.json()
        papers: list[Paper] = []
        for item in payload.get("data") or []:
            paper = self._parse_item(item)
            if paper is not None:
                papers.append(paper)
        return papers

    def _parse_item(self, item: dict[str, Any]) -> Paper | None:
        try:
            paper_id: str | None = item.get("paperId")
            if not paper_id:
                logger.warning("Semantic Scholar item missing paperId, skipping")
                return None

            title: str | None = item.get("title")
            if not title:
                logger.warning("SS item %s has missing or empty title, skipping", paper_id)
                return None

            abstract: str = item.get("abstract") or ""
            raw_authors: list[Any] = item.get("authors") or []
            authors: list[str] = [
                a["name"] for a in raw_authors if isinstance(a, dict) and a.get("name")
            ]

            pub_date_raw: str | None = item.get("publicationDate")
            published_date: date | None = None
            if pub_date_raw:
                try:
                    published_date = date.fromisoformat(pub_date_raw)
                except ValueError:
                    logger.warning(
                        "Invalid date %r for paper %s, setting to None", pub_date_raw, paper_id
                    )

            citation_count: int = int(item.get("citationCount") or 0)
            url: str = item.get("url") or f"https://www.semanticscholar.org/paper/{paper_id}"

            return Paper(
                external_id=paper_id,
                source="semantic_scholar",
                title=title,
                abstract=abstract,
                authors=authors,
                published_date=published_date,
                citation_count=citation_count,
                url=url,
            )
        except (ValidationError, ValueError, KeyError, TypeError) as exc:
            logger.warning("Skipping SS item due to error: %s", exc)
            return None
