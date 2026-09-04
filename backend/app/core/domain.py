"""Domain types for the ViennaCart CVRP MVP.

These models record the Section 22 schema. They do not solve routes.
Business feasibility checks (Check 1, Check 2, Check 3) belong in Phase 2.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class DistanceUnit(StrEnum):
    metres = "metres"


class DistanceSource(StrEnum):
    fixed_matrix = "fixed_matrix"
    haversine_detour = "haversine_detour"


class PrecheckStatus(StrEnum):
    """Outcome of Checks 1–4. This is not a planning-run status."""

    passed = "passed"
    invalid = "invalid"
    infeasible = "infeasible"


class RunType(StrEnum):
    baseline = "baseline"
    optimised = "optimised"


class RunStatus(StrEnum):
    pending = "pending"
    invalid = "invalid"
    infeasible = "infeasible"
    feasible = "feasible"
    heuristic_incomplete = "heuristic_incomplete"
    no_solution_found = "no_solution_found"
    error = "error"


class SolverTermination(StrEnum):
    success = "success"
    timeout = "timeout"
    no_first_solution = "no_first_solution"
    search_exhausted = "search_exhausted"
    not_run = "not_run"
    error = "error"


class NodeType(StrEnum):
    depot = "depot"
    customer = "customer"


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    scenario_name: str
    random_seed: int | None
    depot_id: str
    customer_count: PositiveInt
    vehicle_count: PositiveInt
    vehicle_capacity_totes: PositiveInt
    detour_factor: Decimal = Field(ge=Decimal("1.00"), le=Decimal("2.00"))
    distance_unit: DistanceUnit = DistanceUnit.metres
    distance_source: DistanceSource
    has_geographic_coordinates: bool
    created_at: datetime
    is_synthetic: bool = True


class Depot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    depot_id: str
    scenario_id: str
    name: str
    latitude: float | None = None
    longitude: float | None = None


class Customer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str
    scenario_id: str
    zone_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    demand_totes: PositiveInt


class Vehicle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vehicle_id: str
    scenario_id: str
    capacity_totes: PositiveInt


class PlanningRun(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    scenario_id: str
    run_type: RunType
    status: RunStatus
    comparison_eligible: bool
    unserved_customer_ids: list[str] = Field(default_factory=list)
    partial_distance_metres: int | None = None
    solver_termination: SolverTermination | None = None
    solver_time_limit_seconds: int | None = None
    solver_runtime_seconds: Decimal | None = None
    objective_distance_metres: int | None = None
    vehicles_used: int | None = None
    created_at: datetime


class Route(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    vehicle_id: str
    is_used: bool
    assigned_demand_totes: int = Field(ge=0)
    capacity_totes: PositiveInt
    distance_metres: int = Field(ge=0)
    customer_count: int = Field(ge=0)


class RouteStop(BaseModel):
    """One stop on a reconstructed route.

    `load_after_service_totes` is the operational cumulative load along the
    returned sequence. It is not the MILP potential `w_ik`.
    """

    model_config = ConfigDict(extra="forbid")

    run_id: str
    vehicle_id: str
    sequence_number: int = Field(ge=0)
    node_id: str
    node_type: NodeType
    demand_totes: int = Field(ge=0)
    load_after_service_totes: int = Field(ge=0)
    leg_distance_metres: int = Field(ge=0)
    cumulative_distance_metres: int = Field(ge=0)


class DistanceMatrix(BaseModel):
    """Symmetric integer-metre matrix. Node 0 is the depot."""

    model_config = ConfigDict(extra="forbid")

    node_ids: list[str]
    distances_metres: list[list[int]]


class ScenarioDataset(BaseModel):
    """A fully loaded scenario: master data plus distance matrix."""

    model_config = ConfigDict(extra="forbid")

    scenario: Scenario
    depot: Depot
    customers: list[Customer]
    vehicles: list[Vehicle]
    distance_matrix: DistanceMatrix


class PlanResult(BaseModel):
    """Baseline or optimiser output reconstructed from stop sequences."""

    model_config = ConfigDict(extra="forbid")

    run: PlanningRun
    routes: list[Route]
    stops: list[RouteStop]
    customers_served: int = Field(ge=0)
    demand_served_totes: int = Field(ge=0)
    message: str | None = None


class ScenarioKpis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_orders: int
    customer_orders_served: int
    total_demand_totes: int
    demand_served_totes: int
    vehicles_available: int
    vehicles_used: int
    total_fleet_capacity_totes: int
    total_route_distance_metres: int | None = None
    average_distance_per_delivery_metres: float | None = None
    used_fleet_utilisation: float | None = None
    available_fleet_utilisation: float | None = None
    longest_route_distance_metres: int | None = None
    shortest_non_empty_route_distance_metres: int | None = None
    route_distance_imbalance_metres: int | None = None
    baseline_distance_metres: int | None = None
    optimised_distance_metres: int | None = None
    distance_improvement_percentage: float | None = None


class VehicleKpis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vehicle_id: str
    sequence: list[str]
    customer_count: int
    assigned_demand_totes: int
    capacity_totes: int
    remaining_capacity_totes: int
    capacity_utilisation: float | None = None
    route_distance_metres: int
    is_used: bool


class CustomerResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str
    demand_totes: int
    assigned_vehicle: str | None = None
    route_sequence_position: int | None = None
    previous_node: str | None = None
    next_node: str | None = None
    inbound_leg_distance_metres: int | None = None
    cumulative_route_distance_metres: int | None = None
    service_count: int = 0
    demand_check: str


class ConstraintCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    passed: bool
    message: str
