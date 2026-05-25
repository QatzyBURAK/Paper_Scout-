from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from paper_scout.db.models import Base

DEFAULT_DATABASE_URL = "sqlite:///paper_scout.db"


def make_engine(database_url: str = DEFAULT_DATABASE_URL) -> Engine:
    return create_engine(database_url, echo=False, future=True)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)
    _init_fts(engine)


def _init_fts(engine: Engine) -> None:
    statements = [
        """CREATE VIRTUAL TABLE IF NOT EXISTS papers_fts USING fts5(
            title, abstract,
            content='papers', content_rowid='id',
            tokenize='unicode61 remove_diacritics 2'
        )""",
        """CREATE TRIGGER IF NOT EXISTS papers_ai AFTER INSERT ON papers BEGIN
            INSERT INTO papers_fts(rowid, title, abstract)
            VALUES (new.id, new.title, new.abstract);
        END""",
        """CREATE TRIGGER IF NOT EXISTS papers_ad AFTER DELETE ON papers BEGIN
            INSERT INTO papers_fts(papers_fts, rowid, title, abstract)
            VALUES('delete', old.id, old.title, old.abstract);
        END""",
        """CREATE TRIGGER IF NOT EXISTS papers_au
            AFTER UPDATE OF title, abstract ON papers BEGIN
            INSERT INTO papers_fts(papers_fts, rowid, title, abstract)
            VALUES('delete', old.id, old.title, old.abstract);
            INSERT INTO papers_fts(rowid, title, abstract)
            VALUES (new.id, new.title, new.abstract);
        END""",
    ]
    with engine.begin() as conn:
        for stmt in statements:
            conn.exec_driver_sql(stmt)
