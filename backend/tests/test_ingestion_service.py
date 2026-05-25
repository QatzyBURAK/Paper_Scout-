from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from paper_scout.db import init_db, list_all_papers, make_session_factory
from paper_scout.fetchers.base import Fetcher
from paper_scout.models import Paper
from paper_scout.search.embeddings import FakeEmbedder
from paper_scout.search.semantic import VectorStore
from paper_scout.services.ingestion_service import IngestionService
from paper_scout.services.paper_service import PaperService


class FakeFetcher:
    def __init__(self, source_name: str, papers: list[Paper]) -> None:
        self.source_name = source_name
        self._papers = papers

    def fetch(self, query: str, limit: int, since: date | None = None) -> list[Paper]:
        return self._papers[:limit]


_PAPER_A = Paper(
    external_id="ing-001",
    source="arxiv",
    title="Neural Networks Deep Learning",
    abstract="A study on neural networks.",
    authors=["Alice Smith"],
    published_date=date(2023, 1, 1),
    citation_count=10,
    url="https://arxiv.org/abs/ing-001",
)

_PAPER_B = Paper(
    external_id="ing-002",
    source="arxiv",
    title="Graph Algorithms Survey",
    abstract="Survey on graph algorithms.",
    authors=["Bob Jones"],
    published_date=date(2023, 2, 1),
    citation_count=5,
    url="https://arxiv.org/abs/ing-002",
)

_PAPER_C = Paper(
    external_id="ing-003",
    source="arxiv",
    title="Reinforcement Learning Methods",
    abstract="Methods for reinforcement learning.",
    authors=["Carol White"],
    published_date=date(2023, 3, 1),
    citation_count=8,
    url="https://arxiv.org/abs/ing-003",
)

# Semantic Scholar version of PAPER_A (same title + author, different id/source)
_PAPER_A_S2 = Paper(
    external_id="s2-neural-001",
    source="semantic_scholar",
    title="Neural Networks Deep Learning",
    abstract="Neural networks deep learning overview.",
    authors=["Smith, Alice"],
    published_date=date(2023, 1, 5),
    citation_count=25,
    url="https://s2.org/s2-neural-001",
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
    return VectorStore.open(tmp_path, "ing_test", embedder)


@pytest.fixture
def paper_service(engine: Engine, store: VectorStore) -> PaperService:
    return PaperService(make_session_factory(engine), store)


@pytest.fixture
def ingestion(engine: Engine, paper_service: PaperService) -> IngestionService:
    return IngestionService(
        fetchers=[],
        paper_service=paper_service,
        session_factory=make_session_factory(engine),
    )


def _make_ingestion(
    engine: Engine,
    paper_service: PaperService,
    fetchers: list[Fetcher],
) -> IngestionService:
    return IngestionService(
        fetchers=fetchers,
        paper_service=paper_service,
        session_factory=make_session_factory(engine),
    )


def test_single_source_all_unique(engine: Engine, paper_service: PaperService) -> None:
    svc = _make_ingestion(
        engine, paper_service, [FakeFetcher("arxiv", [_PAPER_A, _PAPER_B, _PAPER_C])]
    )
    report = svc.ingest("test")
    assert report.fetched == 3
    assert report.saved == 3
    assert report.merged == 0
    assert report.fetched == report.saved + report.merged


def test_two_sources_one_duplicate(engine: Engine, paper_service: PaperService) -> None:
    svc = _make_ingestion(
        engine,
        paper_service,
        [
            FakeFetcher("arxiv", [_PAPER_A, _PAPER_B]),
            FakeFetcher("semantic_scholar", [_PAPER_A_S2, _PAPER_C]),
        ],
    )
    report = svc.ingest("test")
    assert report.fetched == 4
    assert report.saved == 3
    assert report.merged == 1
    assert report.fetched == report.saved + report.merged


def test_duplicate_within_batch(engine: Engine, paper_service: PaperService) -> None:
    # Same paper from same source twice in one batch
    svc = _make_ingestion(engine, paper_service, [FakeFetcher("arxiv", [_PAPER_A, _PAPER_A])])
    report = svc.ingest("test")
    assert report.fetched == 2
    assert report.saved == 1
    assert report.merged == 1
    factory = make_session_factory(engine)
    with factory() as session:
        all_papers = list_all_papers(session)
    assert len(all_papers) == 1


def test_existing_db_paper_gets_merged(engine: Engine, paper_service: PaperService) -> None:
    # Seed existing paper in DB
    paper_service.save(_PAPER_A)
    svc = _make_ingestion(engine, paper_service, [FakeFetcher("semantic_scholar", [_PAPER_A_S2])])
    report = svc.ingest("test")
    assert report.fetched == 1
    assert report.saved == 0
    assert report.merged == 1
    # citation_count should be max
    factory = make_session_factory(engine)
    with factory() as session:
        all_papers = list_all_papers(session)
    assert len(all_papers) == 1
    assert all_papers[0].citation_count == max(_PAPER_A.citation_count, _PAPER_A_S2.citation_count)


def test_cumulative_merge_three_copies(engine: Engine, paper_service: PaperService) -> None:
    p5 = Paper(
        external_id="cum-001",
        source="arxiv",
        title="Attention Is All You Need",
        abstract="",
        authors=["Alice Smith"],
        published_date=None,
        citation_count=5,
        url="u1",
    )
    p10 = Paper(
        external_id="cum-002",
        source="arxiv",
        title="Attention Is All You Need",
        abstract="",
        authors=["Smith, Alice"],
        published_date=None,
        citation_count=10,
        url="u2",
    )
    p7 = Paper(
        external_id="cum-003",
        source="semantic_scholar",
        title="Attention is all you need!",
        abstract="",
        authors=["Alice Smith"],
        published_date=None,
        citation_count=7,
        url="u3",
    )
    svc = _make_ingestion(engine, paper_service, [FakeFetcher("arxiv", [p5, p10, p7])])
    svc.ingest("test")
    factory = make_session_factory(engine)
    with factory() as session:
        all_papers = list_all_papers(session)
    assert len(all_papers) == 1
    assert all_papers[0].citation_count == 10


def test_chroma_count_matches_db(
    engine: Engine, paper_service: PaperService, store: VectorStore
) -> None:
    svc = _make_ingestion(
        engine, paper_service, [FakeFetcher("arxiv", [_PAPER_A, _PAPER_B, _PAPER_C])]
    )
    svc.ingest("test")
    factory = make_session_factory(engine)
    with factory() as session:
        db_count = len(list_all_papers(session))
    assert store.count() == db_count


def test_report_invariant(engine: Engine, paper_service: PaperService) -> None:
    svc = _make_ingestion(
        engine,
        paper_service,
        [
            FakeFetcher("arxiv", [_PAPER_A, _PAPER_B]),
            FakeFetcher("semantic_scholar", [_PAPER_A_S2, _PAPER_C]),
        ],
    )
    report = svc.ingest("test")
    assert report.fetched == report.saved + report.merged
