from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date
from pathlib import Path

import httpx
import pytest

from paper_scout.fetchers.semantic_scholar import SemanticScholarFetcher

FIXTURES = Path(__file__).parent / "fixtures"

_Handler = Callable[[httpx.Request], httpx.Response]


class MockTransport(httpx.BaseTransport):
    def __init__(self, handler: _Handler) -> None:
        self._handler = handler

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        return self._handler(request)


def _make_fetcher(handler: _Handler) -> SemanticScholarFetcher:
    return SemanticScholarFetcher(client=httpx.Client(transport=MockTransport(handler)))


def test_parses_full_item() -> None:
    content = (FIXTURES / "semantic_scholar_sample.json").read_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=content)

    papers = _make_fetcher(handler).fetch("transformer", 4)

    assert len(papers) == 2
    full = papers[0]
    assert full.external_id == "abc123def456"
    assert full.title == "Full Featured Paper"
    assert full.abstract == "A complete abstract with all fields present."
    assert full.authors == ["Alice Smith", "Bob Jones"]
    assert full.published_date == date(2024, 3, 15)
    assert full.citation_count == 42
    assert full.url == "https://www.semanticscholar.org/paper/abc123def456"
    assert full.source == "semantic_scholar"


def test_handles_null_fields() -> None:
    content = (FIXTURES / "semantic_scholar_sample.json").read_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=content)

    papers = _make_fetcher(handler).fetch("transformer", 4)

    sparse = papers[1]
    assert sparse.external_id == "def456ghi789"
    assert sparse.abstract == ""
    assert sparse.published_date is None
    assert sparse.citation_count == 0
    assert sparse.url == "https://www.semanticscholar.org/paper/def456ghi789"


def test_skips_item_with_null_title() -> None:
    payload = {
        "total": 1,
        "data": [{"paperId": "xyz", "title": None, "abstract": "no title", "authors": []}],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=json.dumps(payload).encode())

    papers = _make_fetcher(handler).fetch("test", 5)
    assert papers == []


def test_skips_items_without_valid_paper_id() -> None:
    content = (FIXTURES / "semantic_scholar_sample.json").read_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=content)

    papers = _make_fetcher(handler).fetch("transformer", 4)
    assert len(papers) == 2
    ids = {p.external_id for p in papers}
    assert ids == {"abc123def456", "def456ghi789"}


def test_empty_response() -> None:
    content = (FIXTURES / "semantic_scholar_empty.json").read_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=content)

    papers = _make_fetcher(handler).fetch("nothing", 5)
    assert papers == []


def test_timeout_propagates() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    with pytest.raises(httpx.TimeoutException):
        _make_fetcher(handler).fetch("test", 5)
