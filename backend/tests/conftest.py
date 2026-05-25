from __future__ import annotations

from datetime import date

import pytest

from paper_scout.models import Paper


@pytest.fixture
def sample_paper() -> Paper:
    return Paper(
        external_id="2401.00001v1",
        source="arxiv",
        title="Sample Test Paper",
        abstract="This is a test abstract.",
        authors=["Alice Smith", "Bob Jones"],
        published_date=date(2024, 1, 15),
        citation_count=0,
        url="https://arxiv.org/abs/2401.00001v1",
    )
