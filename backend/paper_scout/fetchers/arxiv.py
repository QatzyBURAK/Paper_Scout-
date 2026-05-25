from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from datetime import date

import httpx
from pydantic import ValidationError

from paper_scout.models import Paper

logger = logging.getLogger(__name__)

_ENDPOINT = "https://export.arxiv.org/api/query"
_NS = "{http://www.w3.org/2005/Atom}"
_TIMEOUT = 15.0
_USER_AGENT = "paper-scout/0.1"


def _make_client() -> httpx.Client:
    return httpx.Client(timeout=_TIMEOUT, headers={"User-Agent": _USER_AGENT})


class ArxivFetcher:
    source_name: str = "arxiv"

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client if client is not None else _make_client()

    def close(self) -> None:
        self._client.close()

    def fetch(self, query: str, limit: int, since: date | None = None) -> list[Paper]:
        if not query:
            raise ValueError("query must not be empty")
        if limit <= 0:
            raise ValueError(f"limit must be positive, got {limit}")

        params: dict[str, str | int] = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
        }
        if since is not None:
            params["sortBy"] = "submittedDate"
            params["sortOrder"] = "descending"

        response = self._client.get(_ENDPOINT, params=params)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        papers: list[Paper] = []
        for entry in root.findall(f"{_NS}entry"):
            paper = self._parse_entry(entry)
            if paper is None:
                continue
            if since is not None and (paper.published_date is None or paper.published_date < since):
                continue
            papers.append(paper)
        return papers

    def _parse_entry(self, entry: ET.Element) -> Paper | None:
        try:
            id_elem = entry.find(f"{_NS}id")
            id_url = id_elem.text if id_elem is not None else None
            if not id_url:
                logger.warning("arXiv entry missing <id>, skipping")
                return None
            external_id = id_url.rstrip("/").split("/")[-1]

            title_elem = entry.find(f"{_NS}title")
            title = " ".join((title_elem.text or "").split()) if title_elem is not None else ""

            summary_elem = entry.find(f"{_NS}summary")
            abstract = (summary_elem.text or "").strip() if summary_elem is not None else ""

            authors: list[str] = []
            for author_elem in entry.findall(f"{_NS}author"):
                name_elem = author_elem.find(f"{_NS}name")
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text)

            pub_elem = entry.find(f"{_NS}published")
            pub_text = pub_elem.text if pub_elem is not None else None
            published_date: date | None = None
            if pub_text:
                try:
                    published_date = date.fromisoformat(pub_text[:10])
                except ValueError:
                    logger.warning(
                        "Invalid date %r for entry %s, setting to None", pub_text, external_id
                    )

            return Paper(
                external_id=external_id,
                source="arxiv",
                title=title,
                abstract=abstract,
                authors=authors,
                published_date=published_date,
                citation_count=0,
                url=id_url,
            )
        except (ValidationError, ValueError, AttributeError) as exc:
            logger.warning("Skipping arXiv entry due to error: %s", exc)
            return None
