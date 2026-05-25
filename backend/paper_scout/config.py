from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    db_url: str
    chroma_path: Path
    chroma_collection: str
    embedding_model: str
    cors_origins: list[str]


def load_settings() -> Settings:
    cors_raw = os.getenv("PAPER_SCOUT_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    cors_origins = [o.strip() for o in cors_raw.split(",") if o.strip()]
    return Settings(
        db_url=os.getenv("PAPER_SCOUT_DB_URL", "sqlite:///paper_scout.db"),
        chroma_path=Path(os.getenv("PAPER_SCOUT_CHROMA_PATH", "./chroma_data")),
        chroma_collection=os.getenv("PAPER_SCOUT_CHROMA_COLLECTION", "papers"),
        embedding_model=os.getenv(
            "PAPER_SCOUT_EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        ),
        cors_origins=cors_origins,
    )
