"""Scenario identity, custom planning and capacity-input regression coverage."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.core.generator import generate_scenario
from app.core.invariants import feasible_invariant_errors
from app.core.loader import load_and_precheck
from app.core.optimizer import plan_optimise
from app.main import create_app
from app.storage.duckdb_repo import DuckDBRepository
from scenario_builder import capacity_preview

PARAMETERS = {
    "random_seed": 42,
    "customer_count": 6,
    "vehicle_count": 2,
    "vehicle_capacity_totes": 20,
    "detour_factor": Decimal("1.25"),
    "geographic_zone_weights": {"Z1": 0.25, "Z2": 0.25, "Z3": 0.25, "Z4": 0.25},
}


@pytest.mark.parametrize(
    "change",
    [
        {"random_seed": 43},
        {"customer_count": 7},
        {"vehicle_count": 3},
        {"vehicle_capacity_totes": 21},
        {"detour_factor": Decimal("1.30")},
        {"geographic_zone_weights": {"Z1": 0.5, "Z2": 0.5, "Z3": 0.0, "Z4": 0.0}},
        {"customer_demands": [1, 2, 3, 4, 5, 6]},
    ],
)
def test_all_generation_parameters_change_identity(change):
    _, first = generate_scenario(**PARAMETERS)
    error, changed = generate_scenario(**(PARAMETERS | change))
    assert error is None
    assert first.scenario.scenario_id != changed.scenario.scenario_id


def test_equivalent_parameters_have_stable_identity():
    _, first = generate_scenario(**PARAMETERS)
    _, second = generate_scenario(
        **(
            PARAMETERS
            | {
                "detour_factor": Decimal("1.25"),
                "geographic_zone_weights": {"Z4": 0.25, "Z3": 0.25, "Z2": 0.25, "Z1": 0.25},
            }
        )
    )
    assert first.scenario.scenario_id == second.scenario.scenario_id
    assert first.distance_matrix == second.distance_matrix


@pytest.mark.parametrize("demands", [[1], [1, 2, 3, 4, 5, 0], [1, 2, 3, 4, 5, 1.5]])
def test_invalid_customer_demand_vector_is_rejected(demands):
    error, dataset = generate_scenario(**PARAMETERS, customer_demands=demands)
    assert error is not None
    assert dataset is None


def test_builder_blocks_capacity_errors_but_does_not_claim_packing_feasibility():
    assert not capacity_preview([11, 1], vans=2, capacity=10)["can_generate"]
    assert not capacity_preview([8, 8, 8], vans=2, capacity=10)["can_generate"]
    assert not capacity_preview([None, 2], vans=2, capacity=10)["can_generate"]
    # Three unsplit six-tote orders cannot fit two ten-tote vans, although checks 1/2 pass.
    preview = capacity_preview([6, 6, 6], vans=2, capacity=10)
    assert preview["can_generate"]
    assert preview["minimum_vans"] == 2
    assert preview["spare"] == 2


def test_custom_scenario_plans_stored_demands_and_exports():
    repo = DuckDBRepository(":memory:")
    client = TestClient(create_app(repo=repo))
    request = {**PARAMETERS, "detour_factor": "1.25", "customer_demands": [1, 2, 3, 4, 5, 6]}
    created = client.post("/api/v1/scenarios/generate", json=request)
    assert created.status_code == 200
    scenario_id = created.json()["scenario_id"]
    baseline = client.post("/api/v1/plans/baseline", json={"scenario_id": scenario_id})
    optimised = client.post(
        "/api/v1/plans/optimise",
        json={
            "scenario_id": scenario_id,
            "solver_time_limit_seconds": 1,
        },
    )
    assert baseline.status_code == optimised.status_code == 200
    for response, kind in ((baseline, "baseline"), (optimised, "optimised")):
        run = response.json()
        assert run["run_type"] == kind
        assert run["status"] == "feasible"
        assert run["demand_served_totes"] == 21
        stored = repo.get_run(run["run_id"])
        assert feasible_invariant_errors(stored.dataset, stored.plan) == []
        for extension in ("json", "csv"):
            assert (
                client.get(
                    f"/api/v1/runs/{run['run_id']}/export",
                    params={"format": extension},
                ).status_code
                == 200
            )
    assert baseline.json()["solver_time_limit_seconds"] is None
    assert optimised.json()["solver_time_limit_seconds"] == 1
    assert optimised.json()["distance_improvement_percentage"] is not None
    # Another demand vector is a distinct scenario; it cannot replace this run's source data.
    replacement = client.post(
        "/api/v1/scenarios/generate",
        json={
            **request,
            "customer_demands": [6, 5, 4, 3, 2, 1],
        },
    ).json()
    assert replacement["scenario_id"] != scenario_id
    assert [c.demand_totes for c in repo.get_dataset(scenario_id).customers] == [1, 2, 3, 4, 5, 6]


@pytest.mark.parametrize("scenario_id", ["VIENNA_TIGHT_24", "VIENNA_WIDE_24"])
def test_curated_presets_are_complete_capacity_feasible_cases(scenario_id):
    precheck, dataset = load_and_precheck(scenario_id)
    assert precheck.status.value == "passed"
    assert len(dataset.customers) == 24
    assert sum(c.demand_totes for c in dataset.customers) == 108
    plan = plan_optimise(scenario_id, time_limit_seconds=1)
    assert plan.run.status.value == "feasible"
    assert feasible_invariant_errors(dataset, plan) == []
