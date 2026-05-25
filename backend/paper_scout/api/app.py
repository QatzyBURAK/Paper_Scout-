from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from paper_scout.api.routes.health import router as health_router
from paper_scout.api.routes.ingest import router as ingest_router
from paper_scout.api.routes.papers import router as papers_router
from paper_scout.api.routes.search import router as search_router
from paper_scout.config import load_settings
from paper_scout.db import init_db, make_engine, make_session_factory
from paper_scout.fetchers.arxiv import ArxivFetcher
from paper_scout.fetchers.base import Fetcher
from paper_scout.fetchers.semantic_scholar import SemanticScholarFetcher
from paper_scout.search.embeddings import SentenceTransformerEmbedder
from paper_scout.search.semantic import VectorStore
from paper_scout.services.ingestion_service import IngestionService
from paper_scout.services.paper_service import PaperService
from paper_scout.services.search_service import SearchService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = load_settings()
    engine = make_engine(settings.db_url)
    try:
        init_db(engine)
        session_factory = make_session_factory(engine)
        embedder = SentenceTransformerEmbedder(settings.embedding_model)
        vector_store = VectorStore.open(settings.chroma_path, settings.chroma_collection, embedder)
        paper_service = PaperService(session_factory, vector_store)
        search_service = SearchService(paper_service, session_factory)
        fetchers: list[Fetcher] = [ArxivFetcher(), SemanticScholarFetcher()]
        ingestion_service = IngestionService(fetchers, paper_service, session_factory)

        app.state.engine = engine
        app.state.paper_service = paper_service
        app.state.search_service = search_service
        app.state.ingestion_service = ingestion_service
        yield
    finally:
        engine.dispose()


async def _server_error_handler(request: Request, exc: Exception) -> Response:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def create_app() -> FastAPI:
    settings = load_settings()
    app = FastAPI(
        title="Paper Scout",
        description="AI paper discovery API: arXiv + Semantic Scholar fetching, FTS5 + ChromaDB search.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(Exception, _server_error_handler)
    app.include_router(health_router)
    app.include_router(search_router)
    app.include_router(ingest_router)
    app.include_router(papers_router)
    return app
