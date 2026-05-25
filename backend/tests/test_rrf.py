from __future__ import annotations

from paper_scout.search.hybrid import rrf_combine


def test_empty_rankings_returns_empty() -> None:
    assert rrf_combine([]) == []


def test_all_empty_lists_returns_empty() -> None:
    assert rrf_combine([[], []]) == []


def test_single_ranking_preserves_order() -> None:
    result = rrf_combine([["a", "b", "c"]])
    ids = [id_ for id_, _ in result]
    assert ids == ["a", "b", "c"]


def test_single_ranking_scores_descend() -> None:
    result = rrf_combine([["a", "b", "c"]])
    scores = [s for _, s in result]
    assert scores[0] > scores[1] > scores[2]


def test_overlap_item_ranks_higher_than_single_list() -> None:
    result = rrf_combine([["a", "b", "c"], ["b", "d", "e"]])
    scores = {id_: s for id_, s in result}
    # "b" is in both lists; "a" is only in list1 at rank 1
    assert scores["b"] > scores["a"]
    assert scores["b"] > scores["d"]


def test_k_parameter_affects_absolute_scores() -> None:
    r_k1 = rrf_combine([["a", "b"]], k=1)
    r_k60 = rrf_combine([["a", "b"]], k=60)
    # k=1: 1/2=0.5; k=60: 1/61≈0.016 — k=1 gives higher absolute scores
    assert r_k1[0][1] > r_k60[0][1]
    # Relative order unchanged
    assert r_k1[0][0] == r_k60[0][0] == "a"


def test_deterministic() -> None:
    rankings = [["x", "y", "z"], ["y", "x", "w"]]
    assert rrf_combine(rankings) == rrf_combine(rankings)


def test_in_list_dedup_no_score_inflation() -> None:
    result_dup = rrf_combine([["a", "a", "b"]])
    result_clean = rrf_combine([["a", "b"]])
    scores_dup = {id_: s for id_, s in result_dup}
    scores_clean = {id_: s for id_, s in result_clean}
    # "a" score must be identical — duplicate occurrence must not inflate it
    assert abs(scores_dup["a"] - scores_clean["a"]) < 1e-12
    assert abs(scores_dup["b"] - scores_clean["b"]) < 1e-12


def test_in_list_dedup_output_ids_unique() -> None:
    result = rrf_combine([["a", "a", "b", "a"]])
    ids = [id_ for id_, _ in result]
    assert ids == ["a", "b"]
