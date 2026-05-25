from __future__ import annotations

from paper_scout.db.models import Base, PaperORM, from_orm, to_orm
from paper_scout.db.repository import (
    delete_paper,
    get_paper_by_external_id,
    list_all_papers,
    list_papers_paginated,
    upsert_paper,
)
from paper_scout.db.session import DEFAULT_DATABASE_URL, init_db, make_engine, make_session_factory

__all__ = [
    "DEFAULT_DATABASE_URL",
    "Base",
    "PaperORM",
    "delete_paper",
    "from_orm",
    "get_paper_by_external_id",
    "init_db",
    "list_all_papers",
    "list_papers_paginated",
    "make_engine",
    "make_session_factory",
    "to_orm",
    "upsert_paper",
]
