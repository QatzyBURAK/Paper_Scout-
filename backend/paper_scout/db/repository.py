from __future__ import annotations

from sqlalchemy import delete as sql_delete
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from paper_scout.db.models import PaperORM, from_orm, to_orm
from paper_scout.models import Paper


def upsert_paper(session: Session, paper: Paper) -> PaperORM:
    existing = session.execute(
        select(PaperORM).where(PaperORM.external_id == paper.external_id)
    ).scalar_one_or_none()

    if existing is None:
        orm = to_orm(paper)
        session.add(orm)
        session.flush()
        return orm

    existing.source = paper.source
    existing.title = paper.title
    existing.abstract = paper.abstract
    existing.authors = list(paper.authors)
    existing.published_date = paper.published_date
    existing.citation_count = paper.citation_count
    existing.url = paper.url
    session.flush()
    return existing


def delete_paper(session: Session, external_id: str) -> bool:
    result = session.execute(sql_delete(PaperORM).where(PaperORM.external_id == external_id))
    session.flush()
    return (result.rowcount or 0) > 0


def list_all_papers(session: Session) -> list[Paper]:
    orms = session.scalars(select(PaperORM)).all()
    return [from_orm(o) for o in orms]


def get_paper_by_external_id(session: Session, external_id: str) -> Paper | None:
    orm = session.scalars(select(PaperORM).where(PaperORM.external_id == external_id)).first()
    return from_orm(orm) if orm is not None else None


def list_papers_paginated(session: Session, limit: int, offset: int) -> list[Paper]:
    orms = session.scalars(select(PaperORM).offset(offset).limit(limit)).all()
    return [from_orm(o) for o in orms]


def count_papers(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(PaperORM)) or 0
