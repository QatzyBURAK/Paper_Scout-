from __future__ import annotations

from fastapi.testclient import TestClient

from paper_scout.api.app import create_app

EXPECTED_PATHS = {
    "/health",
    "/papers",
    "/papers/{external_id}",
    "/search/keyword",
    "/search/semantic",
    "/search/hybrid",
    "/ingest",
}


def test_docs_endpoint_returns_200() -> None:
    app = create_app()
    client = TestClient(app)
    r = client.get("/docs")
    assert r.status_code == 200


def test_openapi_json_returns_200() -> None:
    app = create_app()
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200


def test_openapi_contains_all_paths() -> None:
    app = create_app()
    client = TestClient(app)
    r = client.get("/openapi.json")
    paths = set(r.json()["paths"].keys())
    assert paths >= EXPECTED_PATHS


def test_openapi_metadata() -> None:
    app = create_app()
    client = TestClient(app)
    r = client.get("/openapi.json")
    info = r.json()["info"]
    assert info["title"] == "Paper Scout"
    assert info["version"] == "0.1.0"
