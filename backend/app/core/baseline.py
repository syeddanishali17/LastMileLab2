"""Capacity-aware sequential nearest-neighbour baseline (specification Section 15)."""

from __future__ import annotations

from app.core.distance_matrix import matrix_lookup
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


def _choose_next_customer(
    current_node: str,
    candidates: list[str],
    dataset: ScenarioDataset,
) -> str:
    return min(
        candidates,
        key=lambda customer_id: (
            matrix_lookup(dataset.distance_matrix, current_node, customer_id),
            customer_id,
        ),
    )


def build_nearest_neighbour(dataset: ScenarioDataset, run_id: str | None = None) -> PlanResult:
    """Construct routes. Caller must only use this after pre-checks passed."""

    depot_id = dataset.depot.depot_id
    demand = {customer.customer_id: customer.demand_totes for customer in dataset.customers}
    unserved = set(demand)
    sequences: dict[str, list[str]] = {}
    vehicles = sorted(dataset.vehicles, key=lambda vehicle: vehicle.vehicle_id)

    for vehicle in vehicles:
        if not unserved:
            sequences[vehicle.vehicle_id] = unused_vehicle_sequence(depot_id)
            continue
        remaining = vehicle.capacity_totes
        current = depot_id
        sequence = [depot_id]
        while True:
            candidates = [
                customer_id for customer_id in unserved if demand[customer_id] <= remaining
            ]
            if not candidates:
                break
            chosen = _choose_next_customer(current, candidates, dataset)
            sequence.append(chosen)
            remaining -= demand[chosen]
            unserved.remove(chosen)
            current = chosen
        sequence.append(depot_id)
        sequences[vehicle.vehicle_id] = sequence

    unserved_ids = sorted(unserved)
    if unserved_ids:
        status = RunStatus.heuristic_incomplete
        comparison_eligible = False
        message = "Baseline constructed a partial plan. Improvement percentage is not defined."
    else:
        status = RunStatus.feasible
        comparison_eligible = True
        message = "Complete nearest-neighbour plan."

    return assemble_plan(
        dataset=dataset,
        run_type=RunType.baseline,
        status=status,
        comparison_eligible=comparison_eligible,
        vehicle_sequences=sequences,
        unserved_customer_ids=unserved_ids,
        solver_termination=SolverTermination.not_run,
        message=message,
        run_id=run_id,
    )


def plan_baseline(
    scenario_id: str,
    run_id: str | None = None,
    *,
    dataset: ScenarioDataset | None = None,
) -> PlanResult:
    from app.core.validation import precheck_dataset

    if dataset is None:
        precheck, dataset = load_and_precheck(scenario_id)
    else:
        precheck = precheck_dataset(dataset)
    if precheck.status is PrecheckStatus.invalid:
        return empty_plan(
            scenario_id=scenario_id,
            run_type=RunType.baseline,
            status=RunStatus.invalid,
            message="Data integrity failed (Check 4). Baseline was not run.",
            run_id=run_id,
        )
    if precheck.status is PrecheckStatus.infeasible:
        return empty_plan(
            scenario_id=scenario_id,
            run_type=RunType.baseline,
            status=RunStatus.infeasible,
            message="Check 1 or Check 2 failed. Baseline was not run.",
            run_id=run_id,
        )
    if dataset is None:
        return empty_plan(
            scenario_id=scenario_id,
            run_type=RunType.baseline,
            status=RunStatus.error,
            message="Pre-checks passed but the scenario dataset was missing.",
            run_id=run_id,
        )
    return build_nearest_neighbour(dataset, run_id=run_id)
