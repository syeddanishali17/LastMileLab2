"""Constraint reconciliation from reconstructed routes, not from MILP potentials."""

from __future__ import annotations

from app.core.domain import ConstraintCheck, PlanResult, RunStatus, ScenarioDataset
from app.core.invariants import feasible_invariant_errors
from app.core.kpis import compute_customer_results


def reconcile_plan(dataset: ScenarioDataset, plan: PlanResult) -> list[ConstraintCheck]:
    customers = compute_customer_results(dataset, plan)
    demand_pass = all(item.service_count == 1 and item.demand_check == "Pass" for item in customers)
    if plan.run.status is RunStatus.feasible:
        demand_pass = demand_pass and plan.customers_served == len(dataset.customers)
        demand_pass = demand_pass and plan.demand_served_totes == sum(
            customer.demand_totes for customer in dataset.customers
        )

    invariant_errors = []
    if plan.run.status is RunStatus.feasible:
        invariant_errors = feasible_invariant_errors(dataset, plan)

    capacity_ok = all(
        route.assigned_demand_totes <= route.capacity_totes for route in plan.routes
    )
    distance_ok = all(
        route.distance_metres == sum(
            stop.leg_distance_metres for stop in plan.stops if stop.vehicle_id == route.vehicle_id
        )
        for route in plan.routes
    )
    depot_ok = True
    if plan.routes:
        depot_id = dataset.depot.depot_id
        for route in plan.routes:
            stops = [
                stop
                for stop in sorted(plan.stops, key=lambda item: item.sequence_number)
                if stop.vehicle_id == route.vehicle_id
            ]
            if not stops:
                depot_ok = False
                break
            if stops[0].node_id != depot_id or stops[-1].node_id != depot_id:
                depot_ok = False
                break

    if plan.run.status in {RunStatus.invalid, RunStatus.infeasible, RunStatus.error}:
        demand_pass = False
        capacity_ok = False
        distance_ok = False
        depot_ok = False

    checks = [
        ConstraintCheck(
            code="DEMAND_SATISFACTION",
            name="demand_satisfaction",
            passed=demand_pass,
            message=(
                "every customer was assigned exactly once"
                if demand_pass
                else "one or more customers were not served exactly once"
            ),
        ),
        ConstraintCheck(
            code="CAPACITY",
            name="vehicle_capacity",
            passed=capacity_ok
            and not any("exceeds capacity" in error for error in invariant_errors),
            message=(
                "no vehicle exceeded tote capacity"
                if capacity_ok
                else "at least one vehicle exceeds tote capacity"
            ),
        ),
        ConstraintCheck(
            code="DISTANCE",
            name="distance_reconciliation",
            passed=distance_ok and not any("distance" in error for error in invariant_errors),
            message=(
                "route distances reconcile with the distance matrix"
                if distance_ok
                else "a route distance does not match the sum of matrix legs"
            ),
        ),
        ConstraintCheck(
            code="DEPOT_CONNECTIVITY",
            name="depot_connectivity",
            passed=depot_ok,
            message=(
                "every reconstructed route starts and ends at the depot"
                if depot_ok
                else "a route is not depot-connected"
            ),
        ),
    ]
    if plan.run.status is RunStatus.feasible:
        checks.append(
            ConstraintCheck(
                code="INVARIANTS",
                name="solution_invariants",
                passed=invariant_errors == [],
                message=(
                    "all feasible-solution invariants passed"
                    if not invariant_errors
                    else "; ".join(invariant_errors)
                ),
            )
        )
    return checks
