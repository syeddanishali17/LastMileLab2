"""HTTP client for the FastAPI backend. No optimisation logic lives here."""

import atexit
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
load_dotenv()

DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"


class ApiError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        kind: str = "unknown",
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.kind = kind
        self.code = code


def is_missing_run(exc: ApiError) -> bool:
    """True only for a genuine stored-run 404 (UNKNOWN_RUN), not offline or scenario 404."""
    if exc.kind != "not_found":
        return False
    if exc.code == "UNKNOWN_SCENARIO":
        return False
    if exc.code == "UNKNOWN_RUN":
        return True
    text = str(exc)
    if "UNKNOWN_SCENARIO" in text:
        return False
    return "UNKNOWN_RUN" in text or ("Run '" in text and "was not found" in text)


def backend_url() -> str:
    return os.getenv("BACKEND_URL", DEFAULT_BACKEND_URL).rstrip("/")


@lru_cache(maxsize=1)
def _client() -> httpx.Client:
    client = httpx.Client()
    atexit.register(client.close)
    return client


def _error_parts(response: httpx.Response) -> tuple[str, str | None]:
    try:
        payload = response.json()
    except ValueError:
        return f"HTTP {response.status_code}: {response.text}", None
    if not isinstance(payload, dict):
        return str(payload), None
    message = payload.get("message") or payload.get("detail") or response.text
    code = payload.get("code")
    code_text = str(code) if code else None
    if code_text:
        return f"{code_text}: {message}", code_text
    return str(message), None


def _raise_http_error(response: httpx.Response) -> None:
    kind = "unknown"
    if response.status_code == 404:
        kind = "not_found"
    elif response.status_code == 400:
        kind = "invalid"
    elif response.status_code >= 500:
        kind = "server"
    message, code = _error_parts(response)
    raise ApiError(
        message,
        status_code=response.status_code,
        kind=kind,
        code=code,
    )


def request_json(
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    timeout: float = 90.0,
) -> Any:
    url = f"{backend_url()}{path}"
    try:
        response = _client().request(
            method,
            url,
            json=json,
            params=params,
            timeout=timeout,
        )
    except httpx.ConnectError as exc:
        raise ApiError("Planning service unavailable.", kind="connection") from exc
    except httpx.TimeoutException as exc:
        raise ApiError(
            "The API did not respond in time. If you just started an optimisation, "
            "wait a few seconds and retry.",
            kind="timeout",
        ) from exc
    except httpx.HTTPError as exc:
        raise ApiError(str(exc), kind="unknown") from exc
    if response.status_code >= 400:
        _raise_http_error(response)
    if response.headers.get("content-type", "").startswith("application/json"):
        return response.json()
    return response.content


def get_health() -> dict[str, Any]:
    return request_json("GET", "/health", timeout=5.0)


def list_scenarios() -> list[dict[str, Any]]:
    payload = request_json("GET", "/api/v1/scenarios")
    return list(payload.get("scenarios", []))


def get_scenario(scenario_id: str) -> dict[str, Any]:
    return request_json("GET", f"/api/v1/scenarios/{scenario_id}")


def validate_scenario(scenario_id: str) -> dict[str, Any]:
    return request_json("POST", "/api/v1/scenarios/validate", json={"scenario_id": scenario_id})


def generate_scenario(payload: dict[str, Any]) -> dict[str, Any]:
    return request_json("POST", "/api/v1/scenarios/generate", json=payload)


def run_baseline(scenario_id: str) -> dict[str, Any]:
    return request_json("POST", "/api/v1/plans/baseline", json={"scenario_id": scenario_id})


def run_optimise(scenario_id: str, solver_time_limit_seconds: int = 5) -> dict[str, Any]:
    return request_json(
        "POST",
        "/api/v1/plans/optimise",
        json={
            "scenario_id": scenario_id,
            "solver_time_limit_seconds": solver_time_limit_seconds,
        },
        timeout=120.0,
    )


def get_run(run_id: str) -> dict[str, Any]:
    return request_json("GET", f"/api/v1/runs/{run_id}")


def get_routes(run_id: str) -> dict[str, Any]:
    return request_json("GET", f"/api/v1/runs/{run_id}/routes")


def get_checks(run_id: str) -> dict[str, Any]:
    return request_json("GET", f"/api/v1/runs/{run_id}/checks")


def export_run(run_id: str, fmt: str = "json") -> tuple[bytes, str, str]:
    url = f"{backend_url()}/api/v1/runs/{run_id}/export"
    try:
        response = _client().get(url, params={"format": fmt}, timeout=60.0)
    except httpx.ConnectError as exc:
        raise ApiError("Planning service unavailable.", kind="connection") from exc
    except httpx.TimeoutException as exc:
        raise ApiError(
            "The export request timed out. Retry once the run has finished.",
            kind="timeout",
        ) from exc
    except httpx.HTTPError as exc:
        raise ApiError(str(exc), kind="unknown") from exc
    if response.status_code >= 400:
        _raise_http_error(response)
    if fmt == "csv":
        return response.content, "application/zip", f"{run_id}.zip"
    return response.content, "application/json", f"{run_id}.json"
