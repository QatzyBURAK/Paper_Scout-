from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from paper_scout.db.models import PaperORM, from_orm
from paper_scout.models import Paper


def _escape_fts_query(query: str) -> str:
    tokens = query.split()
    quoted = [f'"{t.replace(chr(34), chr(34) * 2)}"' for t in tokens if t]
    return " ".join(quoted)


def search_keyword(session: Session, query: str, limit: int = 20) -> list[Paper]:
    fts_query = _escape_fts_query(query)
    if not fts_query:
        return []
    stmt = select(PaperORM).from_statement(
        text(
            """
            SELECT papers.* FROM papers
            JOIN papers_fts ON papers_fts.rowid = papers.id
            WHERE papers_fts MATCH :q
            ORDER BY bm25(papers_fts)
            LIMIT :lim
            """
        )
    )
    orms = session.scalars(stmt, {"q": fts_query, "lim": limit}).all()
    return [from_orm(o) for o in orms]
