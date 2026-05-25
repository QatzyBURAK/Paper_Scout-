from __future__ import annotations

from paper_scout.api.app import create_app


def test_create_app_registers_routes() -> None:
    app = create_app()
    paths = {r.path for r in app.routes}  # type: ignore[attr-defined]
    assert "/health" in paths
    assert "/search/keyword" in paths
    assert "/search/semantic" in paths
    assert "/search/hybrid" in paths
    assert "/ingest" in paths
    assert "/papers" in paths
    assert "/papers/{external_id}" in paths


def test_create_app_title() -> None:
    app = create_app()
    assert app.title == "Paper Scout"
