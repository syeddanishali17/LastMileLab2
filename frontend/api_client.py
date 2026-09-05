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
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.kind = kind


def backend_url() -> str:
    return os.getenv("BACKEND_URL", DEFAULT_BACKEND_URL).rstrip("/")


@lru_cache(maxsize=1)
def _client() -> httpx.Client:
    client = httpx.Client()
    atexit.register(client.close)
    return client


def _parse_error(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return f"HTTP {response.status_code}: {response.text}"
    message = payload.get("message") or payload.get("detail") or response.text
    code = payload.get("code")
    if code:
        return f"{code}: {message}"
    return str(message)


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
        raise ApiError(
            "Cannot reach the FastAPI backend. Start Uvicorn on port 8000 first. "
            f"Tried {backend_url()}.",
            kind="connection",
        ) from exc
    except httpx.TimeoutException as exc:
        raise ApiError(
            "The API did not respond in time. If you just started an optimisation, "
            "wait a few seconds and retry.",
            kind="timeout",
        ) from exc
    except httpx.HTTPError as exc:
        raise ApiError(str(exc), kind="unknown") from exc
    if response.status_code >= 400:
        kind = "unknown"
        if response.status_code == 404:
            kind = "not_found"
        elif response.status_code == 400:
            kind = "invalid"
        elif response.status_code >= 500:
            kind = "server"
        raise ApiError(
            _parse_error(response),
            status_code=response.status_code,
            kind=kind,
        )
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
        raise ApiError(
            "Cannot reach the FastAPI backend. Start Uvicorn on port 8000 first. "
            f"Tried {backend_url()}.",
            kind="connection",
        ) from exc
    except httpx.TimeoutException as exc:
        raise ApiError(
            "The export request timed out. Retry once the run has finished.",
            kind="timeout",
        ) from exc
    except httpx.HTTPError as exc:
        raise ApiError(str(exc), kind="unknown") from exc
    if response.status_code >= 400:
        kind = "server" if response.status_code >= 500 else "invalid"
        if response.status_code == 404:
            kind = "not_found"
        raise ApiError(
            _parse_error(response),
            status_code=response.status_code,
            kind=kind,
        )
    if fmt == "csv":
        return response.content, "application/zip", f"{run_id}.zip"
    return response.content, "application/json", f"{run_id}.json"
