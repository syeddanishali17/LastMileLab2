"""API response models."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Liveness probe body. This is not a domain run status."""

    status: str = Field(examples=["ok"])
    service: str = Field(examples=["viennacart-cvrp"])


class ErrorBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    code: str
    message: str
    checks: list[dict[str, Any]] = Field(default_factory=list)


class CheckPayload(BaseModel):
    code: str
    name: str
    passed: bool
    hard_fail: bool | None = None
    message: str


class PlanSummaryResponse(BaseModel):
    run_id: str
    run_type: str
    scenario_id: str
    status: str
    comparison_eligible: bool
    solver_termination: str | None = None
    solver_runtime_seconds: float | None = None
    solver_time_limit_seconds: int | None = None
    customers_total: int
    customers_served: int
    unserved_customer_ids: list[str]
    demand_total_totes: int
    demand_served_totes: int
    vehicles_available: int
    vehicles_used: int | None
    total_distance_km: float | None = None
    objective_distance_metres: int | None = None
    partial_distance_metres: int | None = None
    distance_improvement_percentage: float | None = None
    message: str | None = None
