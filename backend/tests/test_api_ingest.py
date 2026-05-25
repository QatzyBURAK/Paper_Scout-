from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from paper_scout.api.app import create_app
from paper_scout.db import init_db, make_session_factory
from paper_scout.models import Paper
from paper_scout.search.embeddings import FakeEmbedder
from paper_scout.search.semantic import VectorStore
from paper_scout.services.ingestion_service import IngestionService
from paper_scout.services.paper_service import PaperService
from paper_scout.services.search_service import SearchService


class FakeFetcher:
    source_name = "arxiv"

    def __init__(self, papers: list[Paper]) -> None:
        self._papers = papers

    def fetch(self, query: str, limit: int, since: date | None = None) -> list[Paper]:
        return self._papers[:limit]


_FAKE_PAPER = Paper(
    external_id="fake-001",
    source="arxiv",
    title="Fake Ingested Paper",
    abstract="Abstract about fake ingestion test.",
    authors=["Tester"],
    published_date=date(2024, 3, 1),
    citation_count=0,
    url="https://arxiv.org/abs/fake-001",
)


@pytest.fixture
def engine() -> Engine:
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(eng)
    return eng


@pytest.fixture
def store(tmp_path: Path) -> VectorStore:
    return VectorStore.open(tmp_path, "api_ingest_test", FakeEmbedder(dim=32))


@pytest.fixture
def paper_service(engine: Engine, store: VectorStore) -> PaperService:
    return PaperService(make_session_factory(engine), store)


@pytest.fixture
def ingestion_service(paper_service: PaperService, engine: Engine) -> IngestionService:
    fetcher = FakeFetcher([_FAKE_PAPER])
    return IngestionService([fetcher], paper_service, make_session_factory(engine))


@pytest.fixture
def search_service(paper_service: PaperService, engine: Engine) -> SearchService:
    return SearchService(paper_service, make_session_factory(engine))


@pytest.fixture
def client(
    ingestion_service: IngestionService,
    search_service: SearchService,
) -> TestClient:
    app = create_app()
    app.state.ingestion_service = ingestion_service
    app.state.search_service = search_service
    return TestClient(app, raise_server_exceptions=True)


def test_ingest_returns_report(client: TestClient) -> None:
    r = client.post("/ingest", json={"query": "transformers", "limit_per_source": 10})
    assert r.status_code == 200
    data = r.json()
    assert "fetched" in data
    assert "saved" in data
    assert "merged" in data
    assert data["fetched"] >= 0


def test_ingest_missing_query_returns_422(client: TestClient) -> None:
    r = client.post("/ingest", json={"limit_per_source": 10})
    assert r.status_code == 422


def test_ingest_empty_query_returns_422(client: TestClient) -> None:
    r = client.post("/ingest", json={"query": "", "limit_per_source": 10})
    assert r.status_code == 422


def test_ingest_limit_over_50_returns_422(client: TestClient) -> None:
    r = client.post("/ingest", json={"query": "x", "limit_per_source": 51})
    assert r.status_code == 422


def test_ingest_limit_zero_returns_422(client: TestClient) -> None:
    r = client.post("/ingest", json={"query": "x", "limit_per_source": 0})
    assert r.status_code == 422


def test_ingest_then_keyword_search_finds_paper(client: TestClient) -> None:
    ingest_r = client.post("/ingest", json={"query": "fake", "limit_per_source": 5})
    assert ingest_r.status_code == 200
    assert ingest_r.json()["saved"] == 1

    search_r = client.get("/search/keyword", params={"q": "fake ingested"})
    assert search_r.status_code == 200
    ids = [p["external_id"] for p in search_r.json()]
    assert "fake-001" in ids
