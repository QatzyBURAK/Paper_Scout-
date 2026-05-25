from __future__ import annotations

from datetime import date

from paper_scout.models import Paper
from paper_scout.services.dedup import (
    _last_name,
    author_overlap,
    is_duplicate,
    merge,
    normalize_title,
)

_P1 = Paper(
    external_id="d001",
    source="arxiv",
    title="Attention Is All You Need",
    abstract="Abstract A",
    authors=["Alice Smith", "Bob Jones"],
    published_date=date(2017, 6, 12),
    citation_count=1000,
    url="https://arxiv.org/abs/1706.03762",
)

_P2 = Paper(
    external_id="d002",
    source="semantic_scholar",
    title="Attention is all you need!",
    abstract="Abstract B",
    authors=["Jones, B.", "Smith, Alice"],
    published_date=date(2017, 6, 1),
    citation_count=1200,
    url="https://s2.org/d002",
)

_P3 = Paper(
    external_id="d003",
    source="arxiv",
    title="Completely Different Paper",
    abstract="Abstract C",
    authors=["Alice Smith"],
    published_date=None,
    citation_count=5,
    url="https://arxiv.org/abs/d003",
)


# --- normalize_title ---


def test_normalize_title_punct_and_case() -> None:
    assert normalize_title("Attention Is All You Need!") == normalize_title(
        "attention is all you need"
    )


def test_normalize_title_whitespace_collapse() -> None:
    assert normalize_title("  AI:  A  Modern  Approach  ") == "ai a modern approach"


def test_normalize_title_hyphen_treated_as_space() -> None:
    assert normalize_title("Graph-based NLP") == normalize_title("graph based nlp")


# --- _last_name ---


def test_last_name_comma_simple() -> None:
    assert _last_name("Smith, J.") == "smith"


def test_last_name_comma_with_full_given() -> None:
    assert _last_name("Smith, John A.") == "smith"


def test_last_name_no_comma_natural_order() -> None:
    assert _last_name("John A. Smith") == "smith"


def test_last_name_single_word() -> None:
    assert _last_name("Smith") == "smith"


def test_last_name_empty() -> None:
    assert _last_name("") == ""


def test_last_name_uppercase_normalized() -> None:
    assert _last_name("JONES, B.") == "jones"


# --- author_overlap ---


def test_author_overlap_comma_vs_natural() -> None:
    assert author_overlap(["Alice Smith", "Bob Jones"], ["Jones, B.", "Carol White"]) == 1


def test_author_overlap_no_match() -> None:
    assert author_overlap(["Alice Smith"], ["Carol White"]) == 0


def test_author_overlap_empty_string_not_counted() -> None:
    assert author_overlap([""], [""]) == 0


# --- is_duplicate ---


def test_is_duplicate_same_title_and_author() -> None:
    assert is_duplicate(_P1, _P2) is True


def test_is_duplicate_same_title_no_matching_author() -> None:
    p = Paper(
        external_id="d099",
        source="arxiv",
        title="Attention is all you need!",
        abstract="",
        authors=["Unknown Stranger"],
        published_date=None,
        citation_count=0,
        url="https://arxiv.org/abs/d099",
    )
    assert is_duplicate(_P1, p) is False


def test_is_duplicate_different_title() -> None:
    assert is_duplicate(_P1, _P3) is False


# --- merge ---


def test_merge_preserves_existing_identity() -> None:
    m = merge(_P1, _P2)
    assert m.external_id == _P1.external_id
    assert m.source == _P1.source
    assert m.url == _P1.url
    assert m.title == _P1.title


def test_merge_citation_count_max() -> None:
    m = merge(_P1, _P2)
    assert m.citation_count == 1200


def test_merge_published_date_earliest() -> None:
    m = merge(_P1, _P2)
    assert m.published_date == date(2017, 6, 1)


def test_merge_published_date_none_handled() -> None:
    m = merge(_P1, _P3)
    assert m.published_date == _P1.published_date


def test_merge_authors_order_preserved_existing_first() -> None:
    existing = Paper(
        external_id="e1",
        source="arxiv",
        title="T",
        abstract="",
        authors=["Alice", "Bob"],
        published_date=None,
        citation_count=0,
        url="u",
    )
    incoming = Paper(
        external_id="e2",
        source="arxiv",
        title="T",
        abstract="",
        authors=["Carol", "Alice"],
        published_date=None,
        citation_count=0,
        url="u2",
    )
    m = merge(existing, incoming)
    assert m.authors == ["Alice", "Bob", "Carol"]


def test_merge_authors_no_alphabetic_sort() -> None:
    existing = Paper(
        external_id="e1",
        source="arxiv",
        title="T",
        abstract="",
        authors=["Zara", "Bob"],
        published_date=None,
        citation_count=0,
        url="u",
    )
    incoming = Paper(
        external_id="e2",
        source="arxiv",
        title="T",
        abstract="",
        authors=["Alice"],
        published_date=None,
        citation_count=0,
        url="u2",
    )
    m = merge(existing, incoming)
    assert m.authors[0] == "Zara"
    assert "Alice" in m.authors
