from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from paper_scout.db import init_db, make_session_factory
from paper_scout.models import Paper
from paper_scout.search.embeddings import FakeEmbedder
from paper_scout.search.semantic import VectorStore
from paper_scout.services.paper_service import PaperService
from paper_scout.services.search_service import SearchService

# keyword-friendly: "transformer" only in FTS5
_KEYWORD = Paper(
    external_id="ss-001",
    source="arxiv",
    title="Transformer Architecture Details",
    abstract="Encoder decoder transformer attention mechanism details.",
    authors=["Alice"],
    published_date=date(2023, 1, 1),
    citation_count=10,
    url="https://arxiv.org/abs/ss-001",
)

# semantic-friendly: shares tokens with the query "graph node embedding"
_SEMANTIC = Paper(
    external_id="ss-002",
    source="arxiv",
    title="Graph Node Embedding Study",
    abstract="Graph nodes and edge embeddings for link prediction.",
    authors=["Bob"],
    published_date=date(2023, 2, 1),
    citation_count=5,
    url="https://arxiv.org/abs/ss-002",
)

# appears in both lists for queries about "neural"
_BOTH = Paper(
    external_id="ss-003",
    source="semantic_scholar",
    title="Neural Network Basics",
    abstract="Introduction to neural networks and backpropagation.",
    authors=["Carol"],
    published_date=date(2023, 3, 1),
    citation_count=50,
    url="https://arxiv.org/abs/ss-003",
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
    return VectorStore.open(tmp_path, "ss_test", embedder)


@pytest.fixture
def paper_service(engine: Engine, store: VectorStore) -> PaperService:
    return PaperService(make_session_factory(engine), store)


@pytest.fixture
def search_service(paper_service: PaperService, engine: Engine) -> SearchService:
    return SearchService(paper_service, make_session_factory(engine))


@pytest.fixture
def populated(paper_service: PaperService) -> None:
    for p in (_KEYWORD, _SEMANTIC, _BOTH):
        paper_service.save(p)


def test_keyword_regression(search_service: SearchService, populated: None) -> None:
    results = search_service.keyword("transformer")
    ids = [p.external_id for p in results]
    assert "ss-001" in ids


def test_semantic_regression(search_service: SearchService, populated: None) -> None:
    results = search_service.semantic("graph node embedding")
    assert len(results) > 0
    assert all(isinstance(r, Paper) for r in results)


def test_hybrid_empty_returns_empty(search_service: SearchService) -> None:
    assert search_service.hybrid("anything") == []


def test_hybrid_returns_papers(search_service: SearchService, populated: None) -> None:
    results = search_service.hybrid("neural network")
    assert len(results) > 0
    assert all(isinstance(r, Paper) for r in results)


def test_hybrid_limit_respected(search_service: SearchService, populated: None) -> None:
    results = search_service.hybrid("neural", limit=1)
    assert len(results) <= 1


def test_hybrid_paper_in_both_lists_ranks_high(
    search_service: SearchService, populated: None
) -> None:
    # "neural" → ss-003 should appear in both keyword and semantic lists
    # and therefore score higher via RRF
    results = search_service.hybrid("neural network backpropagation", per_list_limit=10)
    ids = [p.external_id for p in results]
    assert "ss-003" in ids
    assert ids[0] == "ss-003"


def test_hybrid_no_duplicates(search_service: SearchService, populated: None) -> None:
    results = search_service.hybrid("neural network", per_list_limit=20)
    ids = [p.external_id for p in results]
    assert len(ids) == len(set(ids))
