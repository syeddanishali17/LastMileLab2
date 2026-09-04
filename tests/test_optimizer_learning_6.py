"""OR-Tools LEARNING_6 regression. The 31 km figure is independently enumerated."""

from __future__ import annotations

from app.core.baseline import plan_baseline
from app.core.distance_matrix import metres_to_display_km
from app.core.domain import RunStatus
from app.core.invariants import feasible_invariant_errors
from app.core.loader import load_and_precheck
from app.core.optimizer import plan_optimise
from app.core.routes import node_sequence_for_vehicle


def test_learning_6_optimiser_finds_verified_optimum() -> None:
    _, dataset = load_and_precheck("LEARNING_6")
    assert dataset is not None
    plan = plan_optimise("LEARNING_6", time_limit_seconds=5)
    assert plan.run.status is RunStatus.feasible
    assert plan.run.comparison_eligible is True
    assert plan.run.unserved_customer_ids == []
    assert plan.customers_served == 6
    assert plan.demand_served_totes == 20
    assert plan.run.objective_distance_metres == 31000
    assert metres_to_display_km(31000) == "31.000"
    assert feasible_invariant_errors(dataset, plan) == []
    loads = {
        route.vehicle_id: route.assigned_demand_totes
        for route in plan.routes
        if route.is_used
    }
    assert loads == {"V01": 10, "V02": 10}
    for route in plan.routes:
        if route.is_used:
            sequence = node_sequence_for_vehicle(plan.stops, route.vehicle_id)
            assert sequence[0] == "DEPOT_L6"
            assert sequence[-1] == "DEPOT_L6"


def test_learning_6_baseline_incomplete_does_not_mark_optimiser_infeasible() -> None:
    baseline = plan_baseline("LEARNING_6")
    optimised = plan_optimise("LEARNING_6", time_limit_seconds=5)
    assert baseline.run.status is RunStatus.heuristic_incomplete
    assert optimised.run.status is RunStatus.feasible
    assert optimised.run.status is not RunStatus.infeasible
