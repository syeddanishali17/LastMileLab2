"""Serialise planning runs for the FastAPI contract."""

from __future__ import annotations

from app.core.kpis import metres_to_km
from app.core.pipeline import StoredRun
from app.models.responses import PlanSummaryResponse


def plan_summary(stored: StoredRun) -> PlanSummaryResponse:
    plan = stored.plan
    runtime = plan.run.solver_runtime_seconds
    return PlanSummaryResponse(
        run_id=plan.run.run_id,
        scenario_id=plan.run.scenario_id,
        status=plan.run.status.value,
        comparison_eligible=plan.run.comparison_eligible,
        solver_termination=(
            plan.run.solver_termination.value if plan.run.solver_termination else None
        ),
        solver_runtime_seconds=float(runtime) if runtime is not None else None,
        customers_total=len(stored.dataset.customers),
        customers_served=plan.customers_served,
        unserved_customer_ids=plan.run.unserved_customer_ids,
        demand_total_totes=sum(
            customer.demand_totes for customer in stored.dataset.customers
        ),
        demand_served_totes=plan.demand_served_totes,
        vehicles_available=len(stored.dataset.vehicles),
        vehicles_used=plan.run.vehicles_used,
        total_distance_km=metres_to_km(plan.run.objective_distance_metres),
        objective_distance_metres=plan.run.objective_distance_metres,
        partial_distance_metres=plan.run.partial_distance_metres,
        distance_improvement_percentage=(
            stored.scenario_kpis.distance_improvement_percentage
        ),
        message=plan.message,
    )
