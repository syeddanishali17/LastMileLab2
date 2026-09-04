"""Capacity-aware nearest-neighbour baseline tests."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.core.baseline import build_nearest_neighbour, plan_baseline
from app.core.domain import (
    Customer,
    Depot,
    DistanceMatrix,
    DistanceSource,
    DistanceUnit,
    RunStatus,
    Scenario,
    ScenarioDataset,
    Vehicle,
)
from app.core.routes import node_sequence_for_vehicle


def _dataset(
    *,
    demands: dict[str, int],
    distances: dict[tuple[str, str], int],
    vehicle_ids: list[str],
    capacity: int,
    depot_id: str = "DEPOT",
) -> ScenarioDataset:
    node_ids = [depot_id, *sorted(demands)]
    size = len(node_ids)
    matrix = [[0 for _ in range(size)] for _ in range(size)]
    for i, origin in enumerate(node_ids):
        for j, destination in enumerate(node_ids):
            if i == j:
                continue
            if (origin, destination) in distances:
                matrix[i][j] = distances[(origin, destination)]
            elif (destination, origin) in distances:
                matrix[i][j] = distances[(destination, origin)]
            else:
                matrix[i][j] = 1
    customers = [
        Customer(customer_id=customer_id, scenario_id="TINY", demand_totes=demand)
        for customer_id, demand in demands.items()
    ]
    vehicles = [
        Vehicle(vehicle_id=vehicle_id, scenario_id="TINY", capacity_totes=capacity)
        for vehicle_id in vehicle_ids
    ]
    return ScenarioDataset(
        scenario=Scenario(
            scenario_id="TINY",
            scenario_name="Tiny",
            random_seed=None,
            depot_id=depot_id,
            customer_count=len(customers),
            vehicle_count=len(vehicles),
            vehicle_capacity_totes=capacity,
            detour_factor=Decimal("1.25"),
            distance_unit=DistanceUnit.metres,
            distance_source=DistanceSource.fixed_matrix,
            has_geographic_coordinates=False,
            created_at=datetime.now(UTC),
        ),
        depot=Depot(depot_id=depot_id, scenario_id="TINY", name="Depot"),
        customers=customers,
        vehicles=vehicles,
        distance_matrix=DistanceMatrix(node_ids=node_ids, distances_metres=matrix),
    )


def test_nearest_feasible_customer_is_selected() -> None:
    dataset = _dataset(
        demands={"C1": 1, "C2": 1},
        distances={("DEPOT", "C1"): 10, ("DEPOT", "C2"): 4, ("C1", "C2"): 3},
        vehicle_ids=["V01"],
        capacity=10,
    )
    plan = build_nearest_neighbour(dataset)
    assert node_sequence_for_vehicle(plan.stops, "V01") == ["DEPOT", "C2", "C1", "DEPOT"]


def test_equal_distances_break_ties_by_lowest_customer_id() -> None:
    dataset = _dataset(
        demands={"C1": 1, "C2": 1},
        distances={("DEPOT", "C1"): 5, ("DEPOT", "C2"): 5, ("C1", "C2"): 9},
        vehicle_ids=["V01"],
        capacity=10,
    )
    plan = build_nearest_neighbour(dataset)
    assert node_sequence_for_vehicle(plan.stops, "V01")[1] == "C1"


def test_vehicles_open_in_vehicle_id_order() -> None:
    dataset = _dataset(
        demands={"C1": 5, "C2": 5},
        distances={("DEPOT", "C1"): 1, ("DEPOT", "C2"): 2, ("C1", "C2"): 9},
        vehicle_ids=["V02", "V01"],
        capacity=5,
    )
    plan = build_nearest_neighbour(dataset)
    assert node_sequence_for_vehicle(plan.stops, "V01")[1] == "C1"
    assert node_sequence_for_vehicle(plan.stops, "V02")[1] == "C2"


def test_remaining_capacity_updates_and_new_vehicle_opens() -> None:
    dataset = _dataset(
        demands={"C1": 6, "C2": 6},
        distances={("DEPOT", "C1"): 1, ("DEPOT", "C2"): 8, ("C1", "C2"): 1},
        vehicle_ids=["V01", "V02"],
        capacity=10,
    )
    plan = build_nearest_neighbour(dataset)
    v01 = next(route for route in plan.routes if route.vehicle_id == "V01")
    assert v01.assigned_demand_totes == 6
    assert "C2" not in node_sequence_for_vehicle(plan.stops, "V01")
    assert node_sequence_for_vehicle(plan.stops, "V02")[1] == "C2"


def test_served_customers_are_unique() -> None:
    plan = plan_baseline("LEARNING_6")
    served = [
        stop.node_id
        for stop in plan.stops
        if stop.node_type.value == "customer"
    ]
    assert len(served) == len(set(served))


def test_learning_6_sequential_nn_is_heuristic_incomplete() -> None:
    plan = plan_baseline("LEARNING_6")
    assert plan.run.status is RunStatus.heuristic_incomplete
    assert plan.run.comparison_eligible is False
    assert plan.run.unserved_customer_ids == ["C4"]
    assert plan.run.partial_distance_metres == 27000
    assert plan.run.objective_distance_metres is None
    assert plan.customers_served == 5
    assert plan.demand_served_totes == 15
    assert node_sequence_for_vehicle(plan.stops, "V01") == [
        "DEPOT_L6",
        "C1",
        "C2",
        "C3",
        "DEPOT_L6",
    ]
    assert node_sequence_for_vehicle(plan.stops, "V02") == [
        "DEPOT_L6",
        "C6",
        "C5",
        "DEPOT_L6",
    ]
    loads = {route.vehicle_id: route.assigned_demand_totes for route in plan.routes}
    distances = {route.vehicle_id: route.distance_metres for route in plan.routes}
    assert loads["V01"] == 9
    assert loads["V02"] == 6
    assert distances["V01"] == 16000
    assert distances["V02"] == 11000


def test_infeasible_precheck_does_not_run_baseline() -> None:
    plan = plan_baseline("INFEASIBLE_SINGLE_OVERSIZE")
    assert plan.run.status is RunStatus.infeasible
    assert plan.routes == []
