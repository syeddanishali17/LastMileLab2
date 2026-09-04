"""Domain-model tests. These lock the Section 22 catalogue, not solver behaviour."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.core.domain import (
    Customer,
    Depot,
    PlanningRun,
    RouteStop,
    RunStatus,
    RunType,
    SolverTermination,
    Vehicle,
)


def test_run_status_catalogue_matches_specification() -> None:
    assert {item.value for item in RunStatus} == {
        "pending",
        "invalid",
        "infeasible",
        "feasible",
        "heuristic_incomplete",
        "no_solution_found",
        "error",
    }


def test_solver_termination_catalogue_matches_specification() -> None:
    assert {item.value for item in SolverTermination} == {
        "success",
        "timeout",
        "no_first_solution",
        "search_exhausted",
        "not_run",
        "error",
    }


def test_customer_demand_must_be_a_positive_integer() -> None:
    with pytest.raises(ValidationError):
        Customer(customer_id="C1", scenario_id="LEARNING_6", demand_totes=0)
    with pytest.raises(ValidationError):
        Customer(customer_id="C1", scenario_id="LEARNING_6", demand_totes=-1)


def test_vehicle_capacity_must_be_a_positive_integer() -> None:
    with pytest.raises(ValidationError):
        Vehicle(vehicle_id="V01", scenario_id="LEARNING_6", capacity_totes=0)


def test_learning_6_depot_allows_null_coordinates() -> None:
    depot = Depot(
        depot_id="DEPOT_L6",
        scenario_id="LEARNING_6",
        name="Learning Lab Depot",
        latitude=None,
        longitude=None,
    )
    assert depot.latitude is None
    assert depot.longitude is None


def test_incomplete_baseline_payload_shape() -> None:
    run = PlanningRun(
        run_id="RUN_L6_NN",
        scenario_id="LEARNING_6",
        run_type=RunType.baseline,
        status=RunStatus.heuristic_incomplete,
        comparison_eligible=False,
        unserved_customer_ids=["C4"],
        partial_distance_metres=27000,
        objective_distance_metres=None,
        created_at=datetime.now(UTC),
    )
    assert run.comparison_eligible is False
    assert run.objective_distance_metres is None
    assert run.unserved_customer_ids == ["C4"]


def test_route_stop_load_is_operational_not_mtz_name() -> None:
    stop = RouteStop(
        run_id="RUN_L6_OPT",
        vehicle_id="V01",
        sequence_number=1,
        node_id="C1",
        node_type="customer",
        demand_totes=4,
        load_after_service_totes=4,
        leg_distance_metres=3000,
        cumulative_distance_metres=3000,
    )
    assert stop.load_after_service_totes == 4
    assert not hasattr(stop, "w_ik")
