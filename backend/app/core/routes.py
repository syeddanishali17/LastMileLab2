"""Rebuild routes and stops from a node sequence. Displayed load is operational, not w_ik."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.core.distance_matrix import matrix_lookup
from app.core.domain import (
    NodeType,
    PlanningRun,
    PlanResult,
    Route,
    RouteStop,
    RunStatus,
    RunType,
    ScenarioDataset,
    SolverTermination,
    Vehicle,
)


def new_run_id(run_type: RunType, scenario_id: str) -> str:
    prefix = "BL" if run_type is RunType.baseline else "OPT"
    return f"{prefix}_{scenario_id}_{uuid4().hex[:8]}"


def customer_demand_map(dataset: ScenarioDataset) -> dict[str, int]:
    return {customer.customer_id: customer.demand_totes for customer in dataset.customers}


def node_sequence_for_vehicle(stops: list[RouteStop], vehicle_id: str) -> list[str]:
    ordered = [stop for stop in stops if stop.vehicle_id == vehicle_id]
    ordered.sort(key=lambda stop: stop.sequence_number)
    return [stop.node_id for stop in ordered]


def reconstruct_route(
    run_id: str,
    vehicle: Vehicle,
    node_ids: list[str],
    dataset: ScenarioDataset,
) -> tuple[Route, list[RouteStop]]:
    depot_id = dataset.depot.depot_id
    demands = customer_demand_map(dataset)
    stops: list[RouteStop] = []
    load = 0
    cumulative = 0
    for sequence_number, node_id in enumerate(node_ids):
        if sequence_number == 0:
            leg = 0
        else:
            leg = matrix_lookup(dataset.distance_matrix, node_ids[sequence_number - 1], node_id)
        cumulative += leg
        if node_id == depot_id:
            node_type = NodeType.depot
            demand = 0
        else:
            node_type = NodeType.customer
            demand = demands[node_id]
            load += demand
        stops.append(
            RouteStop(
                run_id=run_id,
                vehicle_id=vehicle.vehicle_id,
                sequence_number=sequence_number,
                node_id=node_id,
                node_type=node_type,
                demand_totes=demand,
                load_after_service_totes=load,
                leg_distance_metres=leg,
                cumulative_distance_metres=cumulative,
            )
        )
    customer_count = sum(1 for stop in stops if stop.node_type is NodeType.customer)
    return (
        Route(
            run_id=run_id,
            vehicle_id=vehicle.vehicle_id,
            is_used=customer_count > 0,
            assigned_demand_totes=load,
            capacity_totes=vehicle.capacity_totes,
            distance_metres=cumulative,
            customer_count=customer_count,
        ),
        stops,
    )


def unused_vehicle_sequence(depot_id: str) -> list[str]:
    return [depot_id, depot_id]


def assemble_plan(
    *,
    dataset: ScenarioDataset,
    run_type: RunType,
    status: RunStatus,
    comparison_eligible: bool,
    vehicle_sequences: dict[str, list[str]],
    unserved_customer_ids: list[str],
    solver_termination: SolverTermination | None,
    solver_time_limit_seconds: int | None = None,
    solver_runtime_seconds: float | None = None,
    message: str | None = None,
    run_id: str | None = None,
) -> PlanResult:
    assigned_run_id = run_id or new_run_id(run_type, dataset.scenario.scenario_id)
    runtime = (
        None
        if solver_runtime_seconds is None
        else Decimal(str(round(solver_runtime_seconds, 4)))
    )
    vehicles = {vehicle.vehicle_id: vehicle for vehicle in dataset.vehicles}
    routes: list[Route] = []
    stops: list[RouteStop] = []
    for vehicle_id in sorted(vehicle_sequences):
        route, route_stops = reconstruct_route(
            assigned_run_id,
            vehicles[vehicle_id],
            vehicle_sequences[vehicle_id],
            dataset,
        )
        routes.append(route)
        stops.extend(route_stops)

    used_routes = [route for route in routes if route.is_used]
    customers_served = sum(route.customer_count for route in used_routes)
    demand_served = sum(route.assigned_demand_totes for route in used_routes)
    total_distance = sum(route.distance_metres for route in used_routes)
    complete = status is RunStatus.feasible
    return PlanResult(
        run=PlanningRun(
            run_id=assigned_run_id,
            scenario_id=dataset.scenario.scenario_id,
            run_type=run_type,
            status=status,
            comparison_eligible=comparison_eligible,
            unserved_customer_ids=sorted(unserved_customer_ids),
            partial_distance_metres=None if complete else total_distance,
            solver_termination=solver_termination,
            solver_time_limit_seconds=solver_time_limit_seconds,
            solver_runtime_seconds=runtime,
            objective_distance_metres=total_distance if complete else None,
            vehicles_used=len(used_routes),
            created_at=datetime.now(UTC),
        ),
        routes=routes,
        stops=stops,
        customers_served=customers_served,
        demand_served_totes=demand_served,
        message=message,
    )


def empty_plan(
    *,
    scenario_id: str,
    run_type: RunType,
    status: RunStatus,
    message: str,
    run_id: str | None = None,
    solver_termination: SolverTermination = SolverTermination.not_run,
) -> PlanResult:
    assigned_run_id = run_id or new_run_id(run_type, scenario_id)
    return PlanResult(
        run=PlanningRun(
            run_id=assigned_run_id,
            scenario_id=scenario_id,
            run_type=run_type,
            status=status,
            comparison_eligible=False,
            unserved_customer_ids=[],
            partial_distance_metres=None,
            solver_termination=solver_termination,
            solver_time_limit_seconds=None,
            solver_runtime_seconds=None,
            objective_distance_metres=None,
            vehicles_used=None,
            created_at=datetime.now(UTC),
        ),
        routes=[],
        stops=[],
        customers_served=0,
        demand_served_totes=0,
        message=message,
    )
