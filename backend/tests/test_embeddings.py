from __future__ import annotations

import math

from paper_scout.search.embeddings import Embedder, FakeEmbedder


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x**2 for x in a))
    norm_b = math.sqrt(sum(x**2 for x in b))
    if norm_a < 1e-12 or norm_b < 1e-12:
        return 0.0
    return dot / (norm_a * norm_b)


def test_fake_embedder_satisfies_protocol() -> None:
    e = FakeEmbedder()
    assert isinstance(e, Embedder)


def test_fake_embedder_deterministic() -> None:
    e = FakeEmbedder()
    assert e.embed(["neural networks"]) == e.embed(["neural networks"])


def test_fake_embedder_l2_norm_is_one() -> None:
    e = FakeEmbedder()
    for text in ["attention mechanism", "deep learning", "graph neural networks"]:
        vec = e.embed([text])[0]
        norm = math.sqrt(sum(x**2 for x in vec))
        assert abs(norm - 1.0) < 1e-9, f"norm={norm} for '{text}'"


def test_fake_embedder_dim_parameter() -> None:
    e = FakeEmbedder(dim=16)
    assert e.dim == 16
    assert len(e.embed(["hello world"])[0]) == 16


def test_fake_embedder_shared_tokens_closer() -> None:
    e = FakeEmbedder()
    v_nn = e.embed(["neural networks"])[0]
    v_na = e.embed(["neural attention"])[0]
    v_bread = e.embed(["potato bread"])[0]
    sim_shared = _cosine(v_nn, v_na)
    sim_none = _cosine(v_nn, v_bread)
    assert sim_shared > sim_none


def test_fake_embedder_empty_string_no_crash() -> None:
    e = FakeEmbedder()
    vec = e.embed([""])[0]
    assert len(vec) == e.dim
    norm = math.sqrt(sum(x**2 for x in vec))
    assert abs(norm - 1.0) < 1e-9


def test_fake_embedder_whitespace_only_no_crash() -> None:
    e = FakeEmbedder()
    vec = e.embed(["   "])[0]
    assert len(vec) == e.dim
    norm = math.sqrt(sum(x**2 for x in vec))
    assert abs(norm - 1.0) < 1e-9


def test_fake_embedder_batch() -> None:
    e = FakeEmbedder()
    texts = ["alpha beta", "gamma delta", "epsilon"]
    vecs = e.embed(texts)
    assert len(vecs) == 3
    for v in vecs:
        assert len(v) == e.dim


def test_fake_embedder_mixed_batch_with_empty() -> None:
    e = FakeEmbedder()
    vecs = e.embed(["neural networks", "", "deep learning"])
    assert len(vecs) == 3
    for v in vecs:
        norm = math.sqrt(sum(x**2 for x in v))
        assert abs(norm - 1.0) < 1e-9
