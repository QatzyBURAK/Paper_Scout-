from __future__ import annotations

import hashlib
import math
from typing import Any, Protocol, cast, runtime_checkable


@runtime_checkable
class Embedder(Protocol):
    @property
    def dim(self) -> int: ...

    def embed(self, texts: list[str]) -> list[list[float]]: ...


def _token_vector(token: str, dim: int) -> list[float]:
    result: list[float] = []
    chunk = 0
    while len(result) < dim:
        payload = token.encode("utf-8") + chunk.to_bytes(2, "big")
        raw = hashlib.blake2b(payload, digest_size=8).digest()
        result.extend(float(b) / 128.0 - 1.0 for b in raw)
        chunk += 1
    return result[:dim]


def _unit_vector(dim: int) -> list[float]:
    return [1.0] + [0.0] * (dim - 1)


class FakeEmbedder:
    """Deterministic, network-free embedder for tests.

    Shared tokens → higher cosine similarity.
    Empty or zero-norm text → returns [1, 0, 0, ...] without crashing.
    """

    def __init__(self, dim: int = 32) -> None:
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        output: list[list[float]] = []
        for text in texts:
            tokens = text.split()
            if not tokens:
                output.append(_unit_vector(self.dim))
                continue
            acc = [0.0] * self.dim
            for token in tokens:
                tv = _token_vector(token.lower(), self.dim)
                for i in range(self.dim):
                    acc[i] += tv[i]
            norm = math.sqrt(sum(x * x for x in acc))
            if norm < 1e-12:
                output.append(_unit_vector(self.dim))
            else:
                output.append([x / norm for x in acc])
        return output


class SentenceTransformerEmbedder:
    """Lazy-loading sentence-transformers embedder for production use."""

    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._model: Any = None

    @property
    def _loaded(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
        return self._model

    @property
    def dim(self) -> int:
        return int(self._loaded.get_sentence_embedding_dimension())

    def embed(self, texts: list[str]) -> list[list[float]]:
        return cast(
            list[list[float]],
            self._loaded.encode(texts, normalize_embeddings=True, convert_to_numpy=True).tolist(),
        )
