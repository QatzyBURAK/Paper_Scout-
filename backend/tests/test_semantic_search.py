from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from paper_scout.models import Paper
from paper_scout.search.embeddings import FakeEmbedder
from paper_scout.search.semantic import VectorStore

_NEURAL = Paper(
    external_id="sem-001",
    source="arxiv",
    title="Neural Networks and Deep Learning",
    abstract="This paper discusses neural networks, backpropagation, and deep architectures.",
    authors=["Alice"],
    published_date=date(2023, 1, 1),
    citation_count=10,
    url="https://arxiv.org/abs/sem-001",
)

_GRAPH = Paper(
    external_id="sem-002",
    source="arxiv",
    title="Graph-based Algorithms",
    abstract="Graph traversal, Dijkstra, and minimum spanning trees.",
    authors=["Bob"],
    published_date=None,
    citation_count=5,
    url="https://arxiv.org/abs/sem-002",
)


@pytest.fixture
def embedder() -> FakeEmbedder:
    return FakeEmbedder(dim=32)


@pytest.fixture
def store(tmp_path: Path, embedder: FakeEmbedder) -> VectorStore:
    return VectorStore.open(tmp_path, "test_papers", embedder)


def test_empty_collection_count(store: VectorStore) -> None:
    assert store.count() == 0


def test_index_paper_increases_count(store: VectorStore) -> None:
    store.index_paper(_NEURAL)
    assert store.count() == 1


def test_index_upsert_idempotent(store: VectorStore) -> None:
    store.index_paper(_NEURAL)
    store.index_paper(_NEURAL)
    assert store.count() == 1


def test_search_returns_nearest_first(store: VectorStore) -> None:
    store.index_paper(_NEURAL)
    store.index_paper(_GRAPH)
    results = store.search("neural networks deep learning backpropagation")
    ids = [id_ for id_, _ in results]
    assert "arxiv:sem-001" in ids
    assert ids[0] == "arxiv:sem-001"


def test_search_empty_collection_returns_empty(store: VectorStore) -> None:
    assert store.search("anything") == []


def test_delete_removes_from_index(store: VectorStore) -> None:
    store.index_paper(_NEURAL)
    store.delete("arxiv:sem-001")
    assert store.count() == 0
    assert store.search("neural networks") == []


def test_search_returns_id_and_distance(store: VectorStore) -> None:
    store.index_paper(_NEURAL)
    results = store.search("neural networks")
    assert len(results) == 1
    paper_id, distance = results[0]
    assert paper_id == "arxiv:sem-001"
    assert isinstance(distance, float)


def test_index_many_bulk(tmp_path: Path, embedder: FakeEmbedder) -> None:
    store = VectorStore.open(tmp_path, "bulk_test", embedder)
    papers = [
        Paper(
            external_id=f"bulk-{i:03d}",
            source="arxiv",
            title=f"Bulk Paper {i}",
            abstract="Test content for bulk indexing.",
            authors=[],
            published_date=None,
            citation_count=0,
            url=f"https://arxiv.org/abs/bulk-{i:03d}",
        )
        for i in range(70)
    ]
    n = store.index_many(papers)
    assert n == 70
    assert store.count() == 70


def test_index_many_idempotent(store: VectorStore) -> None:
    store.index_paper(_NEURAL)
    store.index_paper(_GRAPH)
    store.index_many([_NEURAL, _GRAPH])
    assert store.count() == 2


def test_published_date_none_no_crash(store: VectorStore) -> None:
    store.index_paper(_GRAPH)
    assert store.count() == 1


def test_metadata_source_and_external_id_in_id(store: VectorStore) -> None:
    store.index_paper(_NEURAL)
    results = store.search("neural networks")
    assert len(results) > 0
    paper_id, _ = results[0]
    assert paper_id == "arxiv:sem-001"
