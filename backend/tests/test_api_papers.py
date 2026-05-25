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

_P1 = Paper(
    external_id="papers-001",
    source="arxiv",
    title="First Paper",
    abstract="Abstract of first paper.",
    authors=["Alice"],
    published_date=date(2024, 1, 1),
    citation_count=3,
    url="https://arxiv.org/abs/papers-001",
)
_P2 = Paper(
    external_id="papers-002",
    source="semantic_scholar",
    title="Second Paper",
    abstract="Abstract of second paper.",
    authors=["Bob"],
    published_date=date(2024, 2, 1),
    citation_count=7,
    url="https://arxiv.org/abs/papers-002",
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
def paper_service(engine: Engine, tmp_path: Path) -> PaperService:
    store = VectorStore.open(tmp_path, "api_papers_test", FakeEmbedder(dim=32))
    return PaperService(make_session_factory(engine), store)


@pytest.fixture
def client(paper_service: PaperService) -> TestClient:
    app = create_app()
    app.state.paper_service = paper_service
    app.state.search_service = None
    app.state.ingestion_service = None
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def populated_client(client: TestClient, paper_service: PaperService) -> TestClient:
    paper_service.save(_P1)
    paper_service.save(_P2)
    return client


def test_health_returns_ok(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_papers_empty(client: TestClient) -> None:
    r = client.get("/papers")
    assert r.status_code == 200
    body = r.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["limit"] == 20
    assert body["offset"] == 0


def test_list_papers_returns_all(populated_client: TestClient) -> None:
    r = populated_client.get("/papers")
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 2
    assert body["total"] == 2


def test_list_papers_limit(populated_client: TestClient) -> None:
    r = populated_client.get("/papers", params={"limit": 1})
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 1
    assert body["limit"] == 1
    assert body["total"] == 2


def test_list_papers_offset(populated_client: TestClient) -> None:
    r = populated_client.get("/papers", params={"limit": 10, "offset": 1})
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 1
    assert body["offset"] == 1
    assert body["total"] == 2


def test_list_papers_total_stable_across_offset(
    client: TestClient, paper_service: PaperService
) -> None:
    for i in range(5):
        from datetime import date as _date

        paper_service.save(
            Paper(
                external_id=f"stable-{i:03d}",
                source="arxiv",
                title=f"Paper {i}",
                abstract="Abstract.",
                authors=["Author"],
                published_date=_date(2024, 1, 1),
                citation_count=0,
                url=f"https://arxiv.org/abs/stable-{i:03d}",
            )
        )
    r1 = client.get("/papers", params={"limit": 2, "offset": 0})
    r2 = client.get("/papers", params={"limit": 2, "offset": 2})
    assert r1.json()["total"] == 5
    assert r2.json()["total"] == 5


def test_list_papers_limit_zero_returns_422(client: TestClient) -> None:
    r = client.get("/papers", params={"limit": 0})
    assert r.status_code == 422


def test_list_papers_limit_over_max_returns_422(client: TestClient) -> None:
    r = client.get("/papers", params={"limit": 101})
    assert r.status_code == 422


def test_get_paper_found(populated_client: TestClient) -> None:
    r = populated_client.get("/papers/papers-001")
    assert r.status_code == 200
    assert r.json()["external_id"] == "papers-001"
    assert r.json()["title"] == "First Paper"


def test_get_paper_not_found(client: TestClient) -> None:
    r = client.get("/papers/does-not-exist")
    assert r.status_code == 404
    assert r.json()["detail"] == "Paper not found"
