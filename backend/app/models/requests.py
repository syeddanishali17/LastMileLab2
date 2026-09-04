"""Pydantic request bodies for /api/v1."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ZoneWeights(BaseModel):
    model_config = ConfigDict(extra="forbid")

    Z1: float
    Z2: float
    Z3: float
    Z4: float


class ScenarioIdRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str


class OptimiseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    solver_time_limit_seconds: int = 5


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    random_seed: int = 42
    customer_count: int
    vehicle_count: int
    vehicle_capacity_totes: int
    detour_factor: Decimal = Field(default=Decimal("1.25"))
    geographic_zone_weights: ZoneWeights | None = None
