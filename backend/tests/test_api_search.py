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
from paper_scout.services.paper_service import PaperService
from paper_scout.services.search_service import SearchService

_P1 = Paper(
    external_id="api-001",
    source="arxiv",
    title="Transformer Architecture Details",
    abstract="Encoder decoder transformer attention mechanism.",
    authors=["Alice"],
    published_date=date(2024, 1, 1),
    citation_count=10,
    url="https://arxiv.org/abs/api-001",
)
_P2 = Paper(
    external_id="api-002",
    source="arxiv",
    title="Neural Network Basics",
    abstract="Introduction to neural networks and backpropagation.",
    authors=["Bob"],
    published_date=date(2024, 2, 1),
    citation_count=5,
    url="https://arxiv.org/abs/api-002",
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
    return VectorStore.open(tmp_path, "api_search_test", FakeEmbedder(dim=32))


@pytest.fixture
def paper_service(engine: Engine, store: VectorStore) -> PaperService:
    return PaperService(make_session_factory(engine), store)


@pytest.fixture
def search_service(paper_service: PaperService, engine: Engine) -> SearchService:
    return SearchService(paper_service, make_session_factory(engine))


@pytest.fixture
def client(
    search_service: SearchService,
) -> TestClient:
    app = create_app()
    app.state.search_service = search_service
    # ingestion_service not needed for search tests — set a sentinel
    app.state.ingestion_service = None
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def populated_client(
    client: TestClient,
    paper_service: PaperService,
) -> TestClient:
    paper_service.save(_P1)
    paper_service.save(_P2)
    return client


def test_keyword_returns_match(populated_client: TestClient) -> None:
    r = populated_client.get("/search/keyword", params={"q": "transformer"})
    assert r.status_code == 200
    ids = [p["external_id"] for p in r.json()]
    assert "api-001" in ids


def test_semantic_returns_list(populated_client: TestClient) -> None:
    r = populated_client.get("/search/semantic", params={"q": "neural network"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_hybrid_returns_papers(populated_client: TestClient) -> None:
    r = populated_client.get("/search/hybrid", params={"q": "neural network"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert all("external_id" in p for p in data)


def test_keyword_limit_respected(populated_client: TestClient) -> None:
    r = populated_client.get("/search/keyword", params={"q": "a", "limit": 1})
    assert r.status_code == 200
    assert len(r.json()) <= 1


def test_keyword_empty_q_returns_422(client: TestClient) -> None:
    r = client.get("/search/keyword", params={"q": ""})
    assert r.status_code == 422


def test_keyword_missing_q_returns_422(client: TestClient) -> None:
    r = client.get("/search/keyword")
    assert r.status_code == 422


def test_keyword_limit_zero_returns_422(client: TestClient) -> None:
    r = client.get("/search/keyword", params={"q": "x", "limit": 0})
    assert r.status_code == 422


def test_keyword_limit_over_max_returns_422(client: TestClient) -> None:
    r = client.get("/search/keyword", params={"q": "x", "limit": 501})
    assert r.status_code == 422


def test_semantic_empty_q_returns_422(client: TestClient) -> None:
    r = client.get("/search/semantic", params={"q": ""})
    assert r.status_code == 422


def test_hybrid_empty_q_returns_422(client: TestClient) -> None:
    r = client.get("/search/hybrid", params={"q": ""})
    assert r.status_code == 422
