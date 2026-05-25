from __future__ import annotations

from paper_scout.models import Paper
from paper_scout.search.hybrid import rrf_combine
from paper_scout.search.keyword import search_keyword
from paper_scout.services.paper_service import PaperService, SessionFactory


class SearchService:
    """Facade for keyword, semantic, and hybrid search.

    Does not access DB or Chroma directly — delegates to PaperService and
    search_keyword, keeping store details out of this layer.
    """

    def __init__(
        self,
        paper_service: PaperService,
        session_factory: SessionFactory,
    ) -> None:
        self._paper_service = paper_service
        self._factory = session_factory

    def keyword(self, query: str, limit: int = 20) -> list[Paper]:
        with self._factory() as session:
            return search_keyword(session, query, limit)

    def semantic(self, query: str, limit: int = 20) -> list[Paper]:
        return self._paper_service.search_semantic(query, limit)

    def hybrid(
        self,
        query: str,
        limit: int = 20,
        per_list_limit: int = 50,
        k: int = 60,
    ) -> list[Paper]:
        kw = self.keyword(query, per_list_limit)
        sem = self.semantic(query, per_list_limit)
        kw_ids = [p.external_id for p in kw]
        sem_ids = [p.external_id for p in sem]
        combined = rrf_combine([kw_ids, sem_ids], k=k)
        by_id = {p.external_id: p for p in [*kw, *sem]}
        return [by_id[eid] for eid, _ in combined[:limit] if eid in by_id]
