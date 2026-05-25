from __future__ import annotations

import pytest
from pydantic import ValidationError

from paper_scout.models import Paper


def test_paper_round_trip(sample_paper: Paper) -> None:
    data = sample_paper.model_dump()
    rebuilt = Paper.model_validate(data)
    assert rebuilt == sample_paper


def test_paper_rejects_unknown_source() -> None:
    with pytest.raises(ValidationError):
        Paper(
            external_id="x1",
            source="biorxiv",
            title="Test",
            abstract="",
            url="https://example.com",
        )


def test_paper_rejects_negative_citation() -> None:
    with pytest.raises(ValidationError):
        Paper(
            external_id="x1",
            source="arxiv",
            title="Test",
            abstract="",
            citation_count=-1,
            url="https://example.com",
        )


def test_paper_immutable(sample_paper: Paper) -> None:
    with pytest.raises(ValidationError):
        sample_paper.title = "Changed"  # type: ignore[misc]

