"""Pre-optimisation validation: Check 1, Check 2, Check 3, and Check 4.

Check 1 and Check 2 are hard feasibility fails (`infeasible`).
Check 4 is data integrity (`invalid`).
Check 3 is informational and never fails the scenario.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.core.domain import DistanceMatrix, PrecheckStatus, ScenarioDataset


class CheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    passed: bool
    hard_fail: bool
    message: str


class PrecheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: str | None
    status: PrecheckStatus
    checks: list[CheckResult]
    minimum_vehicles_by_demand: int | None = None


@dataclass
class RawScenarioInput:
    """Untyped fixture or request payload, inspected by Check 4 before modelling."""

    scenario_id: str | None
    has_geographic_coordinates: bool
    depot: dict[str, Any] | None
    customers: list[dict[str, Any]]
    vehicles: list[dict[str, Any]]
    distance_matrix: DistanceMatrix | None = None
    notes: list[str] = field(default_factory=list)


def _is_finite_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return False
    return math.isfinite(float(value))


def _parse_positive_integer(value: Any, field_name: str) -> tuple[int | None, str | None]:
    if isinstance(value, bool):
        return None, f"{field_name} must be a positive integer, not a boolean"
    if isinstance(value, int):
        if value <= 0:
            return None, f"{field_name} must be a positive integer"
        return value, None
    if isinstance(value, float):
        if not value.is_integer():
            return None, f"{field_name} must be a positive integer, not a decimal"
        if value <= 0:
            return None, f"{field_name} must be a positive integer"
        return int(value), None
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return None, f"{field_name} is missing"
        if any(char in stripped for char in ".eE"):
            return None, f"{field_name} must be a positive integer, not a decimal"
        try:
            parsed = int(stripped, 10)
        except ValueError:
            return None, f"{field_name} must be a positive integer"
        if parsed <= 0:
            return None, f"{field_name} must be a positive integer"
        return parsed, None
    return None, f"{field_name} must be a positive integer"


def _valid_wgs84(latitude: Any, longitude: Any) -> bool:
    if not _is_finite_number(latitude) or not _is_finite_number(longitude):
        return False
    return -90.0 <= float(latitude) <= 90.0 and -180.0 <= float(longitude) <= 180.0


def _validate_distance_matrix(
    matrix: DistanceMatrix | None,
    depot_id: str | None,
    customer_ids: list[str],
) -> str | None:
    if matrix is None:
        return "distance matrix is missing"
    size = len(matrix.node_ids)
    expected = 1 + len(customer_ids)
    if size != expected:
        return "matrix dimensions do not match the node count"
    if any(len(row) != size for row in matrix.distances_metres):
        return "distance matrix is not square"
    if len(matrix.distances_metres) != size:
        return "distance matrix is not square"
    if depot_id is not None and (not matrix.node_ids or matrix.node_ids[0] != depot_id):
        return "distance matrix must list the depot as the first node"
    if sorted(matrix.node_ids[1:]) != sorted(customer_ids):
        return "distance matrix nodes do not match the customer set"
    for i, origin in enumerate(matrix.node_ids):
        for j, destination in enumerate(matrix.node_ids):
            value = matrix.distances_metres[i][j]
            if not isinstance(value, int) or isinstance(value, bool):
                return "distances must be non-negative integers in metres"
            if value < 0:
                return "distances must be non-negative integers in metres"
            if i == j and value != 0:
                return "diagonal distances must equal zero"
            if matrix.distances_metres[j][i] != value:
                return "the MVP distance matrix must be symmetric"
    return None


def _check_4(raw: RawScenarioInput) -> CheckResult:
    if raw.depot is None:
        return CheckResult(
            code="CHECK_4",
            name="data_integrity",
            passed=False,
            hard_fail=True,
            message="depot is missing",
        )
    depot_id = raw.depot.get("depot_id")
    if not depot_id:
        return CheckResult(
            code="CHECK_4",
            name="data_integrity",
            passed=False,
            hard_fail=True,
            message="depot is missing",
        )

    customer_ids: list[str] = []
    for customer in raw.customers:
        customer_id = customer.get("customer_id")
        if not customer_id:
            return CheckResult(
                code="CHECK_4",
                name="data_integrity",
                passed=False,
                hard_fail=True,
                message="customer IDs must be present and unique",
            )
        customer_ids.append(str(customer_id))
        _, error = _parse_positive_integer(customer.get("demand_totes"), "demand")
        if error:
            return CheckResult(
                code="CHECK_4",
                name="data_integrity",
                passed=False,
                hard_fail=True,
                message=error,
            )
        if raw.has_geographic_coordinates and not _valid_wgs84(
            customer.get("latitude"),
            customer.get("longitude"),
        ):
            return CheckResult(
                code="CHECK_4",
                name="data_integrity",
                passed=False,
                hard_fail=True,
                message="coordinates must be valid WGS84 numbers",
            )

    if len(customer_ids) != len(set(customer_ids)):
        return CheckResult(
            code="CHECK_4",
            name="data_integrity",
            passed=False,
            hard_fail=True,
            message="customer IDs are not unique",
        )

    vehicle_ids: list[str] = []
    capacities: list[int] = []
    for vehicle in raw.vehicles:
        vehicle_id = vehicle.get("vehicle_id")
        if not vehicle_id:
            return CheckResult(
                code="CHECK_4",
                name="data_integrity",
                passed=False,
                hard_fail=True,
                message="vehicle IDs must be present and unique",
            )
        vehicle_ids.append(str(vehicle_id))
        capacity, error = _parse_positive_integer(vehicle.get("capacity_totes"), "capacity")
        if error or capacity is None:
            return CheckResult(
                code="CHECK_4",
                name="data_integrity",
                passed=False,
                hard_fail=True,
                message=error or "capacity must be a positive integer",
            )
        capacities.append(capacity)

    if len(vehicle_ids) != len(set(vehicle_ids)):
        return CheckResult(
            code="CHECK_4",
            name="data_integrity",
            passed=False,
            hard_fail=True,
            message="vehicle IDs are not unique",
        )
    if not capacities:
        return CheckResult(
            code="CHECK_4",
            name="data_integrity",
            passed=False,
            hard_fail=True,
            message="capacity must be a positive integer",
        )
    if len(set(capacities)) != 1:
        return CheckResult(
            code="CHECK_4",
            name="data_integrity",
            passed=False,
            hard_fail=True,
            message="MVP vehicles must share one tote capacity",
        )

    if raw.has_geographic_coordinates and not _valid_wgs84(
        raw.depot.get("latitude"),
        raw.depot.get("longitude"),
    ):
        return CheckResult(
            code="CHECK_4",
            name="data_integrity",
            passed=False,
            hard_fail=True,
            message="coordinates must be valid WGS84 numbers",
        )

    matrix_error = _validate_distance_matrix(raw.distance_matrix, str(depot_id), customer_ids)
    if matrix_error:
        return CheckResult(
            code="CHECK_4",
            name="data_integrity",
            passed=False,
            hard_fail=True,
            message=matrix_error,
        )

    return CheckResult(
        code="CHECK_4",
        name="data_integrity",
        passed=True,
        hard_fail=True,
        message="data integrity checks passed",
    )


def _demand_values(raw: RawScenarioInput) -> list[int]:
    demands: list[int] = []
    for customer in raw.customers:
        demand, error = _parse_positive_integer(customer.get("demand_totes"), "demand")
        if error or demand is None:
            raise ValueError(error or "demand is invalid")
        demands.append(demand)
    return demands


def _capacity(raw: RawScenarioInput) -> int:
    capacity, error = _parse_positive_integer(raw.vehicles[0].get("capacity_totes"), "capacity")
    if error or capacity is None:
        raise ValueError(error or "capacity is invalid")
    return capacity


def evaluate_prechecks(raw: RawScenarioInput) -> PrecheckResult:
    checks: list[CheckResult] = []
    check_4 = _check_4(raw)
    checks.append(check_4)
    if not check_4.passed:
        return PrecheckResult(
            scenario_id=raw.scenario_id,
            status=PrecheckStatus.invalid,
            checks=checks,
        )

    demands = _demand_values(raw)
    capacity = _capacity(raw)
    vehicle_count = len(raw.vehicles)
    max_demand = max(demands)
    total_demand = sum(demands)
    check_1_passed = max_demand <= capacity
    checks.append(
        CheckResult(
            code="CHECK_1",
            name="individual_demand",
            passed=check_1_passed,
            hard_fail=True,
            message=(
                "maximum customer demand is within vehicle capacity"
                if check_1_passed
                else "maximum customer demand exceeds vehicle capacity"
            ),
        )
    )
    fleet_capacity = vehicle_count * capacity
    check_2_passed = total_demand <= fleet_capacity
    checks.append(
        CheckResult(
            code="CHECK_2",
            name="aggregate_fleet_capacity",
            passed=check_2_passed,
            hard_fail=True,
            message=(
                "total demand is within fleet capacity"
                if check_2_passed
                else "total demand exceeds fleet capacity"
            ),
        )
    )
    minimum_vehicles = math.ceil(total_demand / capacity)
    checks.append(
        CheckResult(
            code="CHECK_3",
            name="theoretical_minimum_vehicles",
            passed=True,
            hard_fail=False,
            message=(
                "minimum vehicles by aggregate demand = "
                f"{minimum_vehicles} (informational; not a feasibility proof)"
            ),
        )
    )
    if check_1_passed and check_2_passed:
        status = PrecheckStatus.passed
    else:
        status = PrecheckStatus.infeasible
    return PrecheckResult(
        scenario_id=raw.scenario_id,
        status=status,
        checks=checks,
        minimum_vehicles_by_demand=minimum_vehicles,
    )


def check_by_code(result: PrecheckResult, code: str) -> CheckResult:
    for check in result.checks:
        if check.code == code:
            return check
    raise KeyError(code)


def precheck_dataset(dataset: ScenarioDataset) -> PrecheckResult:
    raw = RawScenarioInput(
        scenario_id=dataset.scenario.scenario_id,
        has_geographic_coordinates=dataset.scenario.has_geographic_coordinates,
        depot={
            "depot_id": dataset.depot.depot_id,
            "name": dataset.depot.name,
            "latitude": dataset.depot.latitude,
            "longitude": dataset.depot.longitude,
        },
        customers=[
            {
                "customer_id": customer.customer_id,
                "demand_totes": customer.demand_totes,
                "zone_id": customer.zone_id,
                "latitude": customer.latitude,
                "longitude": customer.longitude,
            }
            for customer in dataset.customers
        ],
        vehicles=[
            {
                "vehicle_id": vehicle.vehicle_id,
                "capacity_totes": vehicle.capacity_totes,
            }
            for vehicle in dataset.vehicles
        ],
        distance_matrix=dataset.distance_matrix,
    )
    return evaluate_prechecks(raw)
