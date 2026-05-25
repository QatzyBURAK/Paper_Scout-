from __future__ import annotations

from datetime import date, datetime, timezone
from typing import cast

from sqlalchemy import JSON, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from paper_scout.models import Paper, PaperSource


class Base(DeclarativeBase):
    pass


class PaperORM(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(Text)
    abstract: Mapped[str] = mapped_column(Text, default="")
    authors: Mapped[list[str]] = mapped_column(JSON, default=lambda: [])
    published_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    citation_count: Mapped[int] = mapped_column(Integer, default=0)
    url: Mapped[str] = mapped_column(Text)
    # naive UTC — SQLite has no tz support; contract: value is always UTC
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


def to_orm(paper: Paper) -> PaperORM:
    return PaperORM(
        external_id=paper.external_id,
        source=paper.source,
        title=paper.title,
        abstract=paper.abstract,
        authors=list(paper.authors),
        published_date=paper.published_date,
        citation_count=paper.citation_count,
        url=paper.url,
    )


def from_orm(orm: PaperORM) -> Paper:
    return Paper(
        external_id=orm.external_id,
        source=cast(PaperSource, orm.source),
        title=orm.title,
        abstract=orm.abstract,
        authors=list(orm.authors),
        published_date=orm.published_date,
        citation_count=orm.citation_count,
        url=orm.url,
    )
