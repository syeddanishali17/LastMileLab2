"""Google OR-Tools CVRP solver.

This does not solve the documented three-index MILP. Routes are extracted from
the RoutingModel and reconstructed into x/y/u-equivalent assignments.
"""

from __future__ import annotations

import time

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from app.core.domain import (
    PlanResult,
    PrecheckStatus,
    RunStatus,
    RunType,
    ScenarioDataset,
    SolverTermination,
)
from app.core.loader import load_and_precheck
from app.core.routes import assemble_plan, empty_plan, unused_vehicle_sequence

SUPPORTED_TIME_LIMITS = (1, 5, 10)
DEFAULT_TIME_LIMIT_SECONDS = 5
LEARNING_6_OPTIMUM_METRES = 31000


def map_ortools_status(
    routing_status: int,
    complete: bool,
) -> tuple[RunStatus, SolverTermination]:
    """Map OR-Tools status to domain status. Never maps a missing plan to infeasible."""

    if complete:
        return RunStatus.feasible, SolverTermination.success
    if routing_status == pywrapcp.RoutingModel.ROUTING_FAIL_TIMEOUT:
        return RunStatus.no_solution_found, SolverTermination.timeout
    if routing_status in {
        pywrapcp.RoutingModel.ROUTING_FAIL,
        pywrapcp.RoutingModel.ROUTING_INFEASIBLE,
        pywrapcp.RoutingModel.ROUTING_NOT_SOLVED,
    }:
        return RunStatus.no_solution_found, SolverTermination.no_first_solution
    if routing_status == pywrapcp.RoutingModel.ROUTING_INVALID:
        return RunStatus.error, SolverTermination.error
    return RunStatus.no_solution_found, SolverTermination.search_exhausted


def _extract_sequences(
    manager: pywrapcp.RoutingIndexManager,
    routing: pywrapcp.RoutingModel,
    solution: pywrapcp.Assignment,
    dataset: ScenarioDataset,
) -> dict[str, list[str]]:
    vehicles = sorted(dataset.vehicles, key=lambda vehicle: vehicle.vehicle_id)
    node_ids = dataset.distance_matrix.node_ids
    sequences: dict[str, list[str]] = {}
    for vehicle_number, vehicle in enumerate(vehicles):
        index = routing.Start(vehicle_number)
        nodes: list[str] = []
        while True:
            nodes.append(node_ids[manager.IndexToNode(index)])
            if routing.IsEnd(index):
                break
            index = solution.Value(routing.NextVar(index))
        if (
            len(nodes) == 2
            and nodes[0] == dataset.depot.depot_id
            and nodes[1] == dataset.depot.depot_id
        ):
            sequences[vehicle.vehicle_id] = unused_vehicle_sequence(dataset.depot.depot_id)
        else:
            sequences[vehicle.vehicle_id] = nodes
    return sequences


def _is_complete(sequences: dict[str, list[str]], dataset: ScenarioDataset) -> bool:
    served: list[str] = []
    depot_id = dataset.depot.depot_id
    for sequence in sequences.values():
        served.extend(node_id for node_id in sequence if node_id != depot_id)
    expected = {customer.customer_id for customer in dataset.customers}
    return sorted(served) == sorted(expected) and len(served) == len(expected)


def run_ortools(
    dataset: ScenarioDataset,
    *,
    time_limit_seconds: int = DEFAULT_TIME_LIMIT_SECONDS,
    run_id: str | None = None,
) -> PlanResult:
    if time_limit_seconds not in SUPPORTED_TIME_LIMITS:
        raise ValueError(
            f"solver_time_limit_seconds must be one of {SUPPORTED_TIME_LIMITS}"
        )

    node_ids = dataset.distance_matrix.node_ids
    demands = [0] * len(node_ids)
    for customer in dataset.customers:
        demands[node_ids.index(customer.customer_id)] = customer.demand_totes
    vehicles = sorted(dataset.vehicles, key=lambda vehicle: vehicle.vehicle_id)
    capacities = [vehicle.capacity_totes for vehicle in vehicles]
    distance_rows = dataset.distance_matrix.distances_metres

    manager = pywrapcp.RoutingIndexManager(len(node_ids), len(vehicles), 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_rows[from_node][to_node]

    def demand_callback(from_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    transit_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_index)
    demand_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_index,
        0,
        capacities,
        True,
        "Capacity",
    )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    cheapest_arc = getattr(routing_enums_pb2.FirstSolutionStrategy, "PATH_CHEAPEST_ARC")
    guided_search = getattr(routing_enums_pb2.LocalSearchMetaheuristic, "GUIDED_LOCAL_SEARCH")
    search_parameters.first_solution_strategy = cheapest_arc
    search_parameters.local_search_metaheuristic = guided_search
    search_parameters.time_limit.FromSeconds(time_limit_seconds)

    started = time.perf_counter()
    try:
        solution = routing.SolveWithParameters(search_parameters)
    except Exception as exc:  # noqa: BLE001 - domain status must record solver crashes
        return empty_plan(
            scenario_id=dataset.scenario.scenario_id,
            run_type=RunType.optimised,
            status=RunStatus.error,
            message=f"Unexpected solver failure: {exc}",
            run_id=run_id,
            solver_termination=SolverTermination.error,
        )
    runtime = time.perf_counter() - started
    routing_status = routing.status()

    if solution is None:
        run_status, termination = map_ortools_status(routing_status, complete=False)
        return assemble_plan(
            dataset=dataset,
            run_type=RunType.optimised,
            status=run_status,
            comparison_eligible=False,
            vehicle_sequences={
                vehicle.vehicle_id: unused_vehicle_sequence(dataset.depot.depot_id)
                for vehicle in vehicles
            },
            unserved_customer_ids=[
                customer.customer_id for customer in dataset.customers
            ],
            solver_termination=termination,
            solver_time_limit_seconds=time_limit_seconds,
            solver_runtime_seconds=runtime,
            message=(
                "No complete plan was found within the configured search limit. "
                "This does not prove the scenario is infeasible."
                if termination is SolverTermination.timeout
                else (
                    "Pre-checks passed. No complete unsplit assignment was found. "
                    "Aggregate fleet capacity is necessary but not sufficient "
                    "when orders cannot be split."
                    if dataset.scenario.scenario_id == "INFEASIBLE_BIN_PACKING"
                    else "Pre-checks passed. The search returned no complete mandatory plan."
                )
            ),
            run_id=run_id,
        )

    sequences = _extract_sequences(manager, routing, solution, dataset)
    complete = _is_complete(sequences, dataset)
    run_status, termination = map_ortools_status(routing_status, complete)
    served: list[str] = []
    depot_id = dataset.depot.depot_id
    for sequence in sequences.values():
        served.extend(node_id for node_id in sequence if node_id != depot_id)
    unserved = sorted(
        customer.customer_id
        for customer in dataset.customers
        if customer.customer_id not in set(served)
    )
    if complete and dataset.scenario.scenario_id == "LEARNING_6":
        message = "Independently verified optimum for LEARNING_6."
    elif complete:
        message = "Best feasible solution found within the configured search limit."
    elif termination is SolverTermination.timeout:
        message = (
            "No complete plan was found within the configured search limit. "
            "This does not prove the scenario is infeasible."
        )
    else:
        message = "Pre-checks passed. The search returned no complete mandatory plan."

    plan = assemble_plan(
        dataset=dataset,
        run_type=RunType.optimised,
        status=run_status,
        comparison_eligible=complete,
        vehicle_sequences=sequences,
        unserved_customer_ids=unserved,
        solver_termination=termination,
        solver_time_limit_seconds=time_limit_seconds,
        solver_runtime_seconds=runtime,
        message=message,
        run_id=run_id,
    )
    if (
        complete
        and dataset.scenario.scenario_id == "LEARNING_6"
        and plan.run.objective_distance_metres != LEARNING_6_OPTIMUM_METRES
    ):
        plan.message = "Best feasible solution found within the configured search limit."
    return plan


def plan_optimise(
    scenario_id: str,
    *,
    time_limit_seconds: int = DEFAULT_TIME_LIMIT_SECONDS,
    run_id: str | None = None,
) -> PlanResult:
    precheck, dataset = load_and_precheck(scenario_id)
    if precheck.status is PrecheckStatus.invalid:
        return empty_plan(
            scenario_id=scenario_id,
            run_type=RunType.optimised,
            status=RunStatus.invalid,
            message="Data integrity failed (Check 4). Solver was not run.",
            run_id=run_id,
        )
    if precheck.status is PrecheckStatus.infeasible:
        return empty_plan(
            scenario_id=scenario_id,
            run_type=RunType.optimised,
            status=RunStatus.infeasible,
            message="Check 1 or Check 2 failed. Solver was not run.",
            run_id=run_id,
        )
    if dataset is None:
        return empty_plan(
            scenario_id=scenario_id,
            run_type=RunType.optimised,
            status=RunStatus.error,
            message="Pre-checks passed but the scenario dataset was missing.",
            run_id=run_id,
        )
    return run_ortools(
        dataset,
        time_limit_seconds=time_limit_seconds,
        run_id=run_id,
    )
