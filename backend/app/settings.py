"""Application settings loaded from environment variables. No secrets are required."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _parse_cors_origins(raw: str) -> list[str]:
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    if not origins:
        return ["http://localhost:8501"]
    if "*" in origins:
        raise ValueError("CORS_ORIGINS must not be '*'. Set explicit Streamlit origins.")
    return origins


def _default_duckdb_path() -> str:
    return str(Path(__file__).resolve().parents[2] / "data" / "runs" / "lastmile.duckdb")


@dataclass(frozen=True)
class Settings:
    backend_url: str
    cors_origins: list[str]
    log_level: str
    duckdb_path: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        backend_url=os.getenv("BACKEND_URL", "http://localhost:8000"),
        cors_origins=_parse_cors_origins(os.getenv("CORS_ORIGINS", "http://localhost:8501")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        duckdb_path=os.getenv("DUCKDB_PATH", _default_duckdb_path()),
    )
