"""KPI and reconciliation tests."""

from __future__ import annotations

from app.core.baseline import plan_baseline
from app.core.domain import RunStatus
from app.core.kpis import compute_scenario_kpis, format_utilisation_pct, metres_to_km
from app.core.loader import load_and_precheck
from app.core.optimizer import plan_optimise
from app.core.pipeline import build_stored_run
from app.core.reconciliation import reconcile_plan


def test_learning_6_optimum_kpis_and_reconciliation() -> None:
    _, dataset = load_and_precheck("LEARNING_6")
    assert dataset is not None
    plan = plan_optimise("LEARNING_6", time_limit_seconds=5)
    stored = build_stored_run(dataset, plan)
    kpis = stored.scenario_kpis
    assert kpis.customer_orders == 6
    assert kpis.customer_orders_served == 6
    assert kpis.total_demand_totes == 20
    assert kpis.demand_served_totes == 20
    assert kpis.vehicles_used == 2
    assert kpis.total_route_distance_metres == 31000
    assert metres_to_km(31000) == 31.0
    assert kpis.used_fleet_utilisation == 1.0
    assert format_utilisation_pct(1.0) == "100.0%"
    assert all(item.service_count == 1 for item in stored.assignments)
    assert all(check.passed for check in stored.checks)
    assert kpis.distance_improvement_percentage is None


def test_learning_6_baseline_has_no_improvement_percentage() -> None:
    _, dataset = load_and_precheck("LEARNING_6")
    assert dataset is not None
    plan = plan_baseline("LEARNING_6")
    kpis = compute_scenario_kpis(dataset, plan)
    assert plan.run.status is RunStatus.heuristic_incomplete
    assert plan.run.comparison_eligible is False
    assert kpis.distance_improvement_percentage is None
    assert kpis.baseline_distance_metres is None
    checks = reconcile_plan(dataset, plan)
    demand = next(check for check in checks if check.code == "DEMAND_SATISFACTION")
    assert demand.passed is False


def test_vienna_complete_comparison_is_calculated() -> None:
    _, dataset = load_and_precheck("VIENNA_STANDARD_24")
    assert dataset is not None
    baseline = plan_baseline("VIENNA_STANDARD_24")
    optimised = plan_optimise("VIENNA_STANDARD_24", time_limit_seconds=5)
    kpis = compute_scenario_kpis(dataset, optimised, baseline_plan=baseline)
    assert baseline.run.comparison_eligible is True
    assert optimised.run.comparison_eligible is True
    assert kpis.baseline_distance_metres == baseline.run.objective_distance_metres
    assert kpis.optimised_distance_metres == optimised.run.objective_distance_metres
    expected = (
        (kpis.baseline_distance_metres - kpis.optimised_distance_metres)
        / kpis.baseline_distance_metres
        * 100
    )
    assert kpis.distance_improvement_percentage == expected
    stored = build_stored_run(dataset, baseline)
    assert stored.scenario_kpis.customer_orders_served == 24
    distance_check = next(check for check in stored.checks if check.code == "DISTANCE")
    assert distance_check.passed is True
