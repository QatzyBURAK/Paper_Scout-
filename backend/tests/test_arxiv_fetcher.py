from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path

import httpx
import pytest

from paper_scout.fetchers.arxiv import ArxivFetcher

FIXTURES = Path(__file__).parent / "fixtures"

_Handler = Callable[[httpx.Request], httpx.Response]


class MockTransport(httpx.BaseTransport):
    def __init__(self, handler: _Handler) -> None:
        self._handler = handler

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        return self._handler(request)


def _make_fetcher(handler: _Handler) -> ArxivFetcher:
    return ArxivFetcher(client=httpx.Client(transport=MockTransport(handler)))


def test_parses_full_entry() -> None:
    content = (FIXTURES / "arxiv_sample.xml").read_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=content)

    papers = _make_fetcher(handler).fetch("transformer", 2)

    assert len(papers) == 2
    p = papers[0]
    assert p.external_id == "2401.00001v1"
    assert p.title == "Attention Is All You Need: A Test Paper"
    assert p.abstract == "This is a test abstract for the first paper with all fields populated."
    assert p.authors == ["Alice Smith", "Bob Jones"]
    assert p.published_date == date(2024, 1, 15)
    assert p.citation_count == 0
    assert p.url == "http://arxiv.org/abs/2401.00001v1"
    assert isinstance(p.url, str)


def test_handles_missing_published_date() -> None:
    content = (FIXTURES / "arxiv_sample.xml").read_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=content)

    papers = _make_fetcher(handler).fetch("transformer", 2)

    assert len(papers) == 2
    assert papers[1].published_date is None


def test_empty_response() -> None:
    empty = (
        b'<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=empty)

    papers = _make_fetcher(handler).fetch("nothing", 10)
    assert papers == []


def test_network_error_propagates() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    with pytest.raises(httpx.HTTPStatusError):
        _make_fetcher(handler).fetch("test", 5)


def test_citation_count_is_zero() -> None:
    content = (FIXTURES / "arxiv_sample.xml").read_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=content)

    papers = _make_fetcher(handler).fetch("transformer", 2)
    assert all(p.citation_count == 0 for p in papers)


def test_params_are_escaped() -> None:
    captured: dict[str, str] = {}
    empty = (
        b'<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
    )

    def handler(request: httpx.Request) -> httpx.Response:
        captured["search_query"] = request.url.params["search_query"]
        return httpx.Response(200, content=empty)

    _make_fetcher(handler).fetch("foo bar", 5)
    assert captured["search_query"] == "all:foo bar"
