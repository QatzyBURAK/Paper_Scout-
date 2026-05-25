from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import chromadb

from paper_scout.models import Paper
from paper_scout.search.embeddings import Embedder


class VectorStore:
    """ChromaDB-backed vector index. SQLite is the source of truth; this is
    the search index only."""

    def __init__(
        self,
        collection: Any,
        embedder: Embedder,
    ) -> None:
        self._collection = collection
        self._embedder = embedder

    @classmethod
    def open(
        cls,
        chroma_path: Path,
        collection_name: str,
        embedder: Embedder,
    ) -> VectorStore:
        client = chromadb.PersistentClient(path=str(chroma_path))
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=None,
        )
        return cls(collection=collection, embedder=embedder)

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def index_paper(self, paper: Paper) -> None:
        paper_id = f"{paper.source}:{paper.external_id}"
        doc = f"{paper.title}\n\n{paper.abstract}"
        meta: dict[str, str | int] = {
            "source": paper.source,
            "external_id": paper.external_id,
            "citation_count": paper.citation_count,
        }
        if paper.published_date is not None:
            meta["published_date"] = paper.published_date.isoformat()
        embedding = self._embedder.embed([doc])
        self._collection.upsert(
            ids=[paper_id],
            embeddings=embedding,
            metadatas=[meta],
            documents=[doc],
        )

    def index_many(self, papers: Iterable[Paper], batch_size: int = 64) -> int:
        total = 0
        batch: list[Paper] = []
        for paper in papers:
            batch.append(paper)
            if len(batch) >= batch_size:
                self._upsert_batch(batch)
                total += len(batch)
                batch = []
        if batch:
            self._upsert_batch(batch)
            total += len(batch)
        return total

    def delete(self, paper_id: str) -> None:
        self._collection.delete(ids=[paper_id])

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def search(self, query: str, limit: int = 20) -> list[tuple[str, float]]:
        n = min(limit, self.count())
        if n == 0:
            return []
        emb = self._embedder.embed([query])
        result = self._collection.query(query_embeddings=emb, n_results=n)
        ids: list[str] = result["ids"][0] if result["ids"] else []
        distances: list[float] = result["distances"][0] if result["distances"] else []
        return list(zip(ids, distances, strict=False))

    def count(self) -> int:
        return int(self._collection.count())

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _upsert_batch(self, papers: list[Paper]) -> None:
        ids = [f"{p.source}:{p.external_id}" for p in papers]
        docs = [f"{p.title}\n\n{p.abstract}" for p in papers]
        embeddings = self._embedder.embed(docs)
        metadatas: list[dict[str, str | int]] = [self._make_metadata(p) for p in papers]
        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=docs,
        )

    @staticmethod
    def _make_metadata(paper: Paper) -> dict[str, str | int]:
        meta: dict[str, str | int] = {
            "source": paper.source,
            "external_id": paper.external_id,
            "citation_count": paper.citation_count,
        }
        if paper.published_date is not None:
            meta["published_date"] = paper.published_date.isoformat()
        return meta
