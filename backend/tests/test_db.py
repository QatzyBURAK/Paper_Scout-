from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone

import pytest
from sqlalchemy import Engine, create_engine, inspect, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from paper_scout.db import (
    PaperORM,
    from_orm,
    init_db,
    make_session_factory,
    to_orm,
    upsert_paper,
)
from paper_scout.models import Paper


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
def session(engine: Engine) -> Iterator[Session]:
    factory = make_session_factory(engine)
    with factory() as s:
        yield s


def test_init_db_creates_table(engine: Engine) -> None:
    assert inspect(engine).has_table("papers")


def test_insert_and_read_back(engine: Engine, sample_paper: Paper) -> None:
    factory = make_session_factory(engine)
    with factory() as s:
        s.add(to_orm(sample_paper))
        s.commit()

    with factory() as s2:
        result = s2.execute(select(PaperORM)).scalar_one()
        paper = from_orm(result)

    assert paper.external_id == sample_paper.external_id
    assert paper.title == sample_paper.title
    assert paper.abstract == sample_paper.abstract
    assert paper.authors == list(sample_paper.authors)
    assert paper.published_date == sample_paper.published_date
    assert paper.citation_count == sample_paper.citation_count
    assert paper.url == sample_paper.url
    assert paper.source == sample_paper.source


def test_upsert_no_duplicate(engine: Engine, sample_paper: Paper) -> None:
    updated = Paper(
        external_id=sample_paper.external_id,
        source=sample_paper.source,
        title="Updated Title",
        abstract=sample_paper.abstract,
        authors=sample_paper.authors,
        published_date=sample_paper.published_date,
        citation_count=99,
        url=sample_paper.url,
    )
    factory = make_session_factory(engine)
    with factory() as s:
        upsert_paper(s, sample_paper)
        upsert_paper(s, updated)
        s.commit()

    with factory() as s2:
        results = s2.execute(select(PaperORM)).scalars().all()

    assert len(results) == 1
    assert results[0].title == "Updated Title"
    assert results[0].citation_count == 99


def test_upsert_inserts_new_when_absent(session: Session, sample_paper: Paper) -> None:
    upsert_paper(session, sample_paper)
    session.commit()

    results = session.execute(select(PaperORM)).scalars().all()
    assert len(results) == 1


def test_round_trip_to_orm_from_orm(sample_paper: Paper) -> None:
    orm = to_orm(sample_paper)
    result = from_orm(orm)
    assert result == sample_paper


def test_authors_persisted_as_list(engine: Engine, sample_paper: Paper) -> None:
    factory = make_session_factory(engine)
    with factory() as s:
        upsert_paper(s, sample_paper)
        s.commit()

    with factory() as s2:
        result = s2.execute(select(PaperORM)).scalar_one()

    assert isinstance(result.authors, list)
    assert result.authors == list(sample_paper.authors)


def test_created_at_is_naive_utc_round_trip(engine: Engine, sample_paper: Paper) -> None:
    before = datetime.now(timezone.utc).replace(tzinfo=None)
    factory = make_session_factory(engine)
    with factory() as s:
        upsert_paper(s, sample_paper)
        s.commit()

    with factory() as s2:
        result = s2.execute(select(PaperORM)).scalar_one()

    assert result.created_at.tzinfo is None
    after = datetime.now(timezone.utc).replace(tzinfo=None)
    assert before <= result.created_at <= after
