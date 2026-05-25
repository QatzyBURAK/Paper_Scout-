from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from paper_scout.db import init_db, make_session_factory
from paper_scout.db.repository import delete_paper
from paper_scout.models import Paper
from paper_scout.search.embeddings import FakeEmbedder
from paper_scout.search.keyword import search_keyword
from paper_scout.search.semantic import VectorStore
from paper_scout.services.paper_service import PaperService

_NEURAL = Paper(
    external_id="svc-001",
    source="arxiv",
    title="Neural Networks Overview",
    abstract="Deep learning with neural networks and backpropagation.",
    authors=["Alice"],
    published_date=date(2023, 1, 1),
    citation_count=10,
    url="https://arxiv.org/abs/svc-001",
)

_GRAPH = Paper(
    external_id="svc-002",
    source="semantic_scholar",
    title="Graph Algorithms Study",
    abstract="Graph traversal and shortest path algorithms in detail.",
    authors=["Bob"],
    published_date=date(2023, 2, 1),
    citation_count=5,
    url="https://arxiv.org/abs/svc-002",
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
def embedder() -> FakeEmbedder:
    return FakeEmbedder(dim=32)


@pytest.fixture
def store(tmp_path: Path, embedder: FakeEmbedder) -> VectorStore:
    return VectorStore.open(tmp_path, "svc_test", embedder)


@pytest.fixture
def service(engine: Engine, store: VectorStore) -> PaperService:
    return PaperService(make_session_factory(engine), store)


def test_save_persists_to_db_and_chroma(service: PaperService, store: VectorStore) -> None:
    service.save(_NEURAL)
    assert store.count() == 1
    results = service.search_semantic("neural networks deep learning")
    assert len(results) > 0
    assert results[0].external_id == "svc-001"


def test_delete_removes_from_db_and_chroma(
    service: PaperService, store: VectorStore, engine: Engine
) -> None:
    service.save(_NEURAL)
    removed = service.delete("svc-001")
    assert removed is True
    assert store.count() == 0
    factory = make_session_factory(engine)
    with factory() as session:
        assert search_keyword(session, "neural") == []


def test_delete_nonexistent_returns_false(service: PaperService) -> None:
    assert service.delete("does-not-exist") is False


def test_index_all_idempotent(service: PaperService, store: VectorStore) -> None:
    service.save(_NEURAL)
    service.save(_GRAPH)
    n1 = service.index_all()
    assert n1 == 2
    assert store.count() == 2
    n2 = service.index_all()
    assert n2 == 2
    assert store.count() == 2


def test_search_semantic_returns_paper_objects(service: PaperService) -> None:
    service.save(_NEURAL)
    service.save(_GRAPH)
    results = service.search_semantic("neural networks backpropagation")
    assert len(results) > 0
    for r in results:
        assert isinstance(r, Paper)


def test_search_semantic_order_by_relevance(service: PaperService) -> None:
    service.save(_NEURAL)
    service.save(_GRAPH)
    results = service.search_semantic("neural deep learning backpropagation networks")
    assert len(results) >= 1
    assert results[0].external_id == "svc-001"


def test_search_semantic_hydration_skips_stale_chroma_ids(
    service: PaperService, store: VectorStore, engine: Engine
) -> None:
    """Chroma entry that no longer exists in DB must be silently dropped."""
    service.save(_NEURAL)
    # delete from DB only, leaving stale Chroma entry
    factory = make_session_factory(engine)
    with factory() as session:
        delete_paper(session, "svc-001")
        session.commit()
    results = service.search_semantic("neural networks")
    assert isinstance(results, list)
    assert all(r.external_id != "svc-001" for r in results)


def test_search_semantic_empty_index_returns_empty(service: PaperService) -> None:
    assert service.search_semantic("anything") == []
