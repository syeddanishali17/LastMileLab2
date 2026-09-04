"""Deterministic synthetic scenario generator (specification Section 14)."""

from __future__ import annotations

import random
from datetime import UTC, datetime
from decimal import Decimal

from app.core.distance_matrix import DEFAULT_DETOUR_FACTOR, build_geographic_matrix
from app.core.domain import (
    Customer,
    Depot,
    DistanceSource,
    DistanceUnit,
    Scenario,
    ScenarioDataset,
    Vehicle,
)

ZONE_ORDER = ("Z1", "Z2", "Z3", "Z4")
ZONE_CENTRES = {
    "Z1": (48.209, 16.377),
    "Z2": (48.246, 16.442),
    "Z3": (48.148, 16.358),
    "Z4": (48.178, 16.471),
}
DEPOT_LATITUDE = 48.1700
DEPOT_LONGITUDE = 16.4400
LAT_BOUNDS = (48.10, 48.32)
LON_BOUNDS = (16.25, 16.55)
DEMAND_UPPER_BOUNDS = (0.05, 0.15, 0.30, 0.50, 0.70, 0.85, 0.95, 1.00)


def clip(value: float, lower: float, upper: float) -> float:
    return min(upper, max(lower, value))


def _demand_from_u(u_demand: float) -> int:
    for totes, upper in enumerate(DEMAND_UPPER_BOUNDS, start=1):
        if u_demand < upper:
            return totes
    return 8


def _select_zone(u_zone: float, weights: dict[str, float]) -> str:
    c1 = weights["Z1"]
    c2 = weights["Z1"] + weights["Z2"]
    c3 = weights["Z1"] + weights["Z2"] + weights["Z3"]
    if u_zone < c1:
        return "Z1"
    if c1 <= u_zone < c2:
        return "Z2"
    if c2 <= u_zone < c3:
        return "Z3"
    return "Z4"


def validate_generator_request(
    *,
    random_seed: int,
    customer_count: int,
    vehicle_count: int,
    vehicle_capacity_totes: int,
    detour_factor: Decimal,
    geographic_zone_weights: dict[str, float],
) -> str | None:
    if not 0 <= random_seed <= 2147483647:
        return "random_seed must be between 0 and 2147483647"
    if not 1 <= customer_count <= 50:
        return "customer_count must be between 1 and 50"
    if not 1 <= vehicle_count <= 10:
        return "vehicle_count must be between 1 and 10"
    if not 1 <= vehicle_capacity_totes <= 100:
        return "vehicle_capacity_totes must be between 1 and 100"
    if detour_factor < Decimal("1.00") or detour_factor > Decimal("2.00"):
        return "detour_factor must be between 1.00 and 2.00"
    if detour_factor.as_tuple().exponent < -2:
        return "detour_factor must have at most two decimal places"
    if set(geographic_zone_weights) != set(ZONE_ORDER):
        return "geographic_zone_weights must include Z1, Z2, Z3, and Z4"
    if any(weight < 0 for weight in geographic_zone_weights.values()):
        return "geographic_zone_weights must be non-negative"
    weight_sum = sum(geographic_zone_weights[zone] for zone in ZONE_ORDER)
    if abs(weight_sum - 1.0) > 1e-9:
        return "geographic_zone_weights must already sum to 1"
    return None


def generate_scenario(
    *,
    random_seed: int = 42,
    customer_count: int,
    vehicle_count: int,
    vehicle_capacity_totes: int,
    detour_factor: Decimal = DEFAULT_DETOUR_FACTOR,
    geographic_zone_weights: dict[str, float] | None = None,
) -> tuple[str | None, ScenarioDataset | None]:
    weights = geographic_zone_weights or {zone: 0.25 for zone in ZONE_ORDER}
    error = validate_generator_request(
        random_seed=random_seed,
        customer_count=customer_count,
        vehicle_count=vehicle_count,
        vehicle_capacity_totes=vehicle_capacity_totes,
        detour_factor=detour_factor,
        geographic_zone_weights=weights,
    )
    if error:
        return error, None

    scenario_id = f"GEN_{random_seed}_{customer_count}_{vehicle_count}"
    rng = random.Random(random_seed)
    customers: list[Customer] = []
    for index in range(1, customer_count + 1):
        u_zone = rng.random()
        u_lat = rng.uniform(-0.015, 0.015)
        u_lon = rng.uniform(-0.015, 0.015)
        u_demand = rng.random()
        zone_id = _select_zone(u_zone, weights)
        centre_lat, centre_lon = ZONE_CENTRES[zone_id]
        customers.append(
            Customer(
                customer_id=f"C{index:03d}",
                scenario_id=scenario_id,
                zone_id=zone_id,
                latitude=clip(centre_lat + u_lat, *LAT_BOUNDS),
                longitude=clip(centre_lon + u_lon, *LON_BOUNDS),
                demand_totes=_demand_from_u(u_demand),
            )
        )
    vehicles = [
        Vehicle(
            vehicle_id=f"V{index:02d}",
            scenario_id=scenario_id,
            capacity_totes=vehicle_capacity_totes,
        )
        for index in range(1, vehicle_count + 1)
    ]
    depot = Depot(
        depot_id="DEPOT_01",
        scenario_id=scenario_id,
        name="ViennaCart Dispatch Depot",
        latitude=DEPOT_LATITUDE,
        longitude=DEPOT_LONGITUDE,
    )
    matrix = build_geographic_matrix(depot, customers, detour_factor)
    dataset = ScenarioDataset(
        scenario=Scenario(
            scenario_id=scenario_id,
            scenario_name=f"Generated {customer_count}-customer dispatch",
            random_seed=random_seed,
            depot_id=depot.depot_id,
            customer_count=customer_count,
            vehicle_count=vehicle_count,
            vehicle_capacity_totes=vehicle_capacity_totes,
            detour_factor=detour_factor,
            distance_unit=DistanceUnit.metres,
            distance_source=DistanceSource.haversine_detour,
            has_geographic_coordinates=True,
            created_at=datetime.now(UTC),
            is_synthetic=True,
        ),
        depot=depot,
        customers=customers,
        vehicles=vehicles,
        distance_matrix=matrix,
    )
    return None, dataset
