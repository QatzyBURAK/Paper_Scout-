from __future__ import annotations

from collections.abc import Iterator
from datetime import date

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from paper_scout.db import init_db, make_session_factory, upsert_paper
from paper_scout.models import Paper
from paper_scout.search import search_keyword

_TRANSFORMER = Paper(
    external_id="fts-001",
    source="arxiv",
    title="Transformer Architecture for NLP",
    abstract="Attention mechanisms enable sequence modelling.",
    authors=["Alice"],
    published_date=date(2023, 1, 1),
    citation_count=10,
    url="https://arxiv.org/abs/fts-001",
)

_NEURAL = Paper(
    external_id="fts-002",
    source="arxiv",
    title="Neural Networks Overview",
    abstract="Deep learning with transformer blocks and attention layers.",
    authors=["Bob"],
    published_date=date(2023, 2, 1),
    citation_count=5,
    url="https://arxiv.org/abs/fts-002",
)

_GRAPH = Paper(
    external_id="fts-003",
    source="semantic_scholar",
    title="Graph Neural Networks",
    abstract="Graph-based machine learning with node embeddings.",
    authors=["Carol"],
    published_date=date(2023, 3, 1),
    citation_count=3,
    url="https://arxiv.org/abs/fts-003",
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
def populated_session(engine: Engine) -> Iterator[Session]:
    factory = make_session_factory(engine)
    with factory() as s:
        for paper in (_TRANSFORMER, _NEURAL, _GRAPH):
            upsert_paper(s, paper)
        s.commit()
        yield s


def test_single_word_match(populated_session: Session) -> None:
    results = search_keyword(populated_session, "transformer")
    ids = [p.external_id for p in results]
    assert "fts-001" in ids
    assert "fts-002" in ids  # abstract also contains "transformer"


def test_multi_word_implicit_and(populated_session: Session) -> None:
    # Both "neural" and "networks" must be present
    results = search_keyword(populated_session, "neural networks")
    ids = [p.external_id for p in results]
    assert "fts-002" in ids
    assert "fts-003" in ids
    assert "fts-001" not in ids


def test_match_in_abstract_only(populated_session: Session) -> None:
    results = search_keyword(populated_session, "embeddings")
    assert len(results) == 1
    assert results[0].external_id == "fts-003"


def test_no_match_returns_empty(populated_session: Session) -> None:
    results = search_keyword(populated_session, "quantumphysics")
    assert results == []


def test_bm25_ranking_title_over_abstract(engine: Engine) -> None:
    # "attention" in title → ranked above "attention" only in abstract
    title_paper = Paper(
        external_id="rank-title",
        source="arxiv",
        title="Attention Mechanism Study",
        abstract="Unrelated content about graphs.",
        authors=[],
        published_date=None,
        citation_count=0,
        url="https://arxiv.org/abs/rank-title",
    )
    abstract_paper = Paper(
        external_id="rank-abstract",
        source="arxiv",
        title="Unrelated Study",
        abstract="Attention mechanism in neural networks.",
        authors=[],
        published_date=None,
        citation_count=0,
        url="https://arxiv.org/abs/rank-abstract",
    )
    factory = make_session_factory(engine)
    with factory() as s:
        upsert_paper(s, title_paper)
        upsert_paper(s, abstract_paper)
        s.commit()

    with factory() as s2:
        results = search_keyword(s2, "attention")

    assert len(results) == 2
    assert results[0].external_id == "rank-title"


def test_special_characters_no_crash(populated_session: Session) -> None:
    dangerous = ['foo" OR 1=1', "AND", "foo(bar)", "*", ":col", 'he said "hi"']
    for q in dangerous:
        results = search_keyword(populated_session, q)
        assert isinstance(results, list)


def test_empty_query_returns_empty(populated_session: Session) -> None:
    assert search_keyword(populated_session, "") == []
    assert search_keyword(populated_session, "   ") == []


def test_limit_respected(populated_session: Session) -> None:
    results = search_keyword(populated_session, "neural", limit=1)
    assert len(results) <= 1


def test_update_propagates_to_fts(engine: Engine) -> None:
    factory = make_session_factory(engine)
    original = Paper(
        external_id="upd-001",
        source="arxiv",
        title="Old Title about Bananas",
        abstract="Nothing special.",
        authors=[],
        published_date=None,
        citation_count=0,
        url="https://arxiv.org/abs/upd-001",
    )
    updated = Paper(
        external_id="upd-001",
        source="arxiv",
        title="New Title about Quantum",
        abstract="Nothing special.",
        authors=[],
        published_date=None,
        citation_count=0,
        url="https://arxiv.org/abs/upd-001",
    )
    with factory() as s:
        upsert_paper(s, original)
        s.commit()

    with factory() as s:
        upsert_paper(s, updated)
        s.commit()

    with factory() as s:
        assert search_keyword(s, "bananas") == []
        results = search_keyword(s, "quantum")
        assert len(results) == 1
        assert results[0].external_id == "upd-001"


def test_case_insensitive(populated_session: Session) -> None:
    results = search_keyword(populated_session, "TRANSFORMER")
    ids = [p.external_id for p in results]
    assert "fts-001" in ids
