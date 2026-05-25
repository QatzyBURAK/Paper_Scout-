from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from paper_scout.api.app import create_app


@pytest.fixture
def cors_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("PAPER_SCOUT_CORS_ORIGINS", "http://localhost:5173")
    app = create_app()
    return TestClient(app)


def test_cors_preflight_allowed_origin(cors_client: TestClient) -> None:
    r = cors_client.options(
        "/search/keyword",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_preflight_disallowed_origin(cors_client: TestClient) -> None:
    r = cors_client.options(
        "/search/keyword",
        headers={
            "Origin": "http://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.headers.get("access-control-allow-origin") != "http://evil.example"
