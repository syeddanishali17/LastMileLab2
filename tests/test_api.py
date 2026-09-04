"""API contract tests."""

from __future__ import annotations

import io
import zipfile

from fastapi.testclient import TestClient

from app.core.domain import PlanResult, RunStatus, RunType, SolverTermination
from app.core.routes import empty_plan
from app.main import create_app
from app.settings import get_settings
from app.storage.duckdb_repo import DuckDBRepository


def _client() -> TestClient:
    return TestClient(create_app(repo=DuckDBRepository(":memory:")))


def test_health_returns_http_200() -> None:
    response = _client().get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "viennacart-cvrp"


def test_health_is_outside_api_v1_prefix() -> None:
    client = _client()
    assert client.get("/health").status_code == 200
    assert client.get("/api/v1/health").status_code == 404


def test_cors_origins_are_explicit() -> None:
    origins = get_settings().cors_origins
    assert origins
    assert "*" not in origins


def test_known_scenario_loads_successfully() -> None:
    response = _client().get("/api/v1/scenarios/LEARNING_6")
    assert response.status_code == 200
    body = response.json()
    assert body["scenario"]["scenario_id"] == "LEARNING_6"
    assert body["precheck"]["status"] == "passed"


def test_unknown_scenario_returns_http_404() -> None:
    response = _client().get("/api/v1/scenarios/MISSING")
    assert response.status_code == 404
    body = response.json()
    assert body["status"] == "invalid"
    assert body["code"] == "UNKNOWN_SCENARIO"


def test_invalid_generator_request_returns_validation_error() -> None:
    response = _client().post(
        "/api/v1/scenarios/generate",
        json={
            "random_seed": 1,
            "customer_count": 51,
            "vehicle_count": 4,
            "vehicle_capacity_totes": 30,
        },
    )
    assert response.status_code == 400
    assert response.json()["status"] == "invalid"


def test_baseline_endpoint_returns_structured_output() -> None:
    response = _client().post(
        "/api/v1/plans/baseline",
        json={"scenario_id": "LEARNING_6"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "heuristic_incomplete"
    assert body["comparison_eligible"] is False
    assert body["unserved_customer_ids"] == ["C4"]
    assert body["partial_distance_metres"] == 27000
    assert body["objective_distance_metres"] is None
    assert body["distance_improvement_percentage"] is None


def test_optimisation_endpoint_returns_structured_output() -> None:
    response = _client().post(
        "/api/v1/plans/optimise",
        json={"scenario_id": "LEARNING_6", "solver_time_limit_seconds": 5},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "feasible"
    assert body["objective_distance_metres"] == 31000
    assert body["total_distance_km"] == 31.0
    assert body["customers_served"] == 6


def test_infeasible_precheck_returns_http_200() -> None:
    response = _client().post(
        "/api/v1/plans/baseline",
        json={"scenario_id": "INFEASIBLE_SINGLE_OVERSIZE"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "infeasible"


def test_run_endpoints_reconcile_with_optimisation_response() -> None:
    client = _client()
    created = client.post(
        "/api/v1/plans/optimise",
        json={"scenario_id": "LEARNING_6", "solver_time_limit_seconds": 5},
    )
    run_id = created.json()["run_id"]
    fetched = client.get(f"/api/v1/runs/{run_id}")
    routes = client.get(f"/api/v1/runs/{run_id}/routes")
    checks = client.get(f"/api/v1/runs/{run_id}/checks")
    assert fetched.status_code == 200
    assert fetched.json()["objective_distance_metres"] == created.json()[
        "objective_distance_metres"
    ]
    assert routes.status_code == 200
    assert routes.json()["run_id"] == run_id
    assert checks.status_code == 200
    assert checks.json()["scenario_id"] == "LEARNING_6"


def test_json_export_includes_scenario_and_run_ids() -> None:
    client = _client()
    created = client.post(
        "/api/v1/plans/baseline",
        json={"scenario_id": "LEARNING_6"},
    )
    run_id = created.json()["run_id"]
    exported = client.get(f"/api/v1/runs/{run_id}/export?format=json")
    assert exported.status_code == 200
    body = exported.json()
    assert body["scenario_id"] == "LEARNING_6"
    assert body["run_id"] == run_id


def test_csv_export_zip_contains_required_files() -> None:
    client = _client()
    created = client.post(
        "/api/v1/plans/baseline",
        json={"scenario_id": "LEARNING_6"},
    )
    run_id = created.json()["run_id"]
    exported = client.get(f"/api/v1/runs/{run_id}/export?format=csv")
    assert exported.status_code == 200
    assert "zip" in exported.headers["content-type"]
    archive = zipfile.ZipFile(io.BytesIO(exported.content))
    assert set(archive.namelist()) == {"assignments.csv", "stops.csv", "vehicles.csv"}
    assignments = archive.read("assignments.csv").decode("utf-8")
    assert "scenario_id" in assignments
    assert "run_id" in assignments
    assert run_id in assignments


def test_solver_timeout_returns_no_solution_found(monkeypatch) -> None:
    def fake_optimise(scenario_id: str, time_limit_seconds: int = 5, run_id=None) -> PlanResult:
        return empty_plan(
            scenario_id=scenario_id,
            run_type=RunType.optimised,
            status=RunStatus.no_solution_found,
            message=(
                "No complete plan was found within the configured search limit. "
                "This does not prove the scenario is infeasible."
            ),
            run_id=run_id,
            solver_termination=SolverTermination.timeout,
        )

    monkeypatch.setattr("app.api.planning.plan_optimise", fake_optimise)
    response = _client().post(
        "/api/v1/plans/optimise",
        json={"scenario_id": "LEARNING_6", "solver_time_limit_seconds": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "no_solution_found"
    assert body["solver_termination"] == "timeout"
    assert body["status"] != "infeasible"
