"""Pytest defaults. Use an in-memory DuckDB so tests do not write lastmile.duckdb."""

from __future__ import annotations

import os

os.environ["DUCKDB_PATH"] = ":memory:"

from app.settings import get_settings  # noqa: E402

get_settings.cache_clear()
