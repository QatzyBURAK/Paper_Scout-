from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from paper_scout.db.models import PaperORM, from_orm
from paper_scout.db.repository import (
    count_papers,
    delete_paper,
    get_paper_by_external_id,
    list_all_papers,
    list_papers_paginated,
    upsert_paper,
)
from paper_scout.models import Paper
from paper_scout.search.semantic import VectorStore

SessionFactory = sessionmaker[Session] | Callable[[], Session]


class PaperService:
    """Coordinates SQLite (source of truth) and ChromaDB (vector index)."""

    def __init__(self, session_factory: SessionFactory, vector_store: VectorStore) -> None:
        self._factory = session_factory
        self._vector = vector_store

    def save(self, paper: Paper) -> None:
        with self._factory() as session:
            upsert_paper(session, paper)
            session.commit()
        self._vector.index_paper(paper)

    def delete(self, external_id: str) -> bool:
        with self._factory() as session:
            existing = get_paper_by_external_id(session, external_id)
            if existing is None:
                return False
            paper_id = f"{existing.source}:{external_id}"
            removed = delete_paper(session, external_id)
            session.commit()
        if removed:
            self._vector.delete(paper_id)
        return removed

    def index_all(self) -> int:
        with self._factory() as session:
            papers = list_all_papers(session)
        return self._vector.index_many(papers)

    def save_many(self, papers: list[Paper]) -> None:
        if not papers:
            return
        with self._factory() as session:
            for p in papers:
                upsert_paper(session, p)
            session.commit()
        self._vector.index_many(papers)

    def get(self, external_id: str) -> Paper | None:
        with self._factory() as session:
            return get_paper_by_external_id(session, external_id)

    def list_paginated(self, limit: int, offset: int) -> list[Paper]:
        with self._factory() as session:
            return list_papers_paginated(session, limit, offset)

    def count(self) -> int:
        with self._factory() as session:
            return count_papers(session)

    def search_semantic(self, query: str, limit: int = 20) -> list[Paper]:
        hits = self._vector.search(query, limit)
        if not hits:
            return []
        # id format: "source:external_id" — split on first ":" only
        external_ids = [id_.split(":", 1)[1] for id_, _ in hits]
        with self._factory() as session:
            orms = session.scalars(
                select(PaperORM).where(PaperORM.external_id.in_(external_ids))
            ).all()
        by_ext = {o.external_id: from_orm(o) for o in orms}
        # preserve Chroma distance order; silently drop ids absent from DB
        return [by_ext[eid] for eid in external_ids if eid in by_ext]
