"""Build a stored planning run: plan + KPIs + reconciliation."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.domain import (
    ConstraintCheck,
    CustomerResult,
    PlanResult,
    ScenarioDataset,
    ScenarioKpis,
    VehicleKpis,
)
from app.core.kpis import compute_customer_results, compute_scenario_kpis, compute_vehicle_kpis
from app.core.reconciliation import reconcile_plan


@dataclass
class StoredRun:
    dataset: ScenarioDataset
    plan: PlanResult
    scenario_kpis: ScenarioKpis
    vehicle_kpis: list[VehicleKpis]
    assignments: list[CustomerResult]
    checks: list[ConstraintCheck]


def build_stored_run(
    dataset: ScenarioDataset,
    plan: PlanResult,
    *,
    baseline_plan: PlanResult | None = None,
) -> StoredRun:
    return StoredRun(
        dataset=dataset,
        plan=plan,
        scenario_kpis=compute_scenario_kpis(dataset, plan, baseline_plan=baseline_plan),
        vehicle_kpis=compute_vehicle_kpis(dataset, plan),
        assignments=compute_customer_results(dataset, plan),
        checks=reconcile_plan(dataset, plan),
    )
