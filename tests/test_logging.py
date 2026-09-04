"""Structured logging helpers."""

from __future__ import annotations

import json
import logging

from fastapi.testclient import TestClient

from app.logging_config import JsonFormatter, configure_logging
from app.main import create_app
from app.storage.duckdb_repo import DuckDBRepository


def test_json_formatter_includes_level_and_message() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="http_request",
        args=(),
        exc_info=None,
    )
    record.http_path = "/health"
    payload = json.loads(formatter.format(record))
    assert payload["level"] == "INFO"
    assert payload["message"] == "http_request"
    assert payload["http_path"] == "/health"
    assert "timestamp" in payload


def test_health_request_succeeds_after_logging_setup() -> None:
    configure_logging("INFO")
    client = TestClient(create_app(repo=DuckDBRepository(":memory:")))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("x-request-id")
