"""Distance-matrix construction for the ViennaCart CVRP MVP.

Geographic distances are synthetic Haversine estimates with a detour factor.
They are not live road or traffic measurements.
"""

from __future__ import annotations

import math
from decimal import Decimal

from app.core.domain import Customer, Depot, DistanceMatrix

EARTH_RADIUS_M = 6371000
DEFAULT_DETOUR_FACTOR = Decimal("1.25")
SYNTHETIC_DISTANCE_LABEL = (
    "Estimated synthetic distance. This is not a live road or traffic measurement."
)


def round_half_up(value: float) -> int:
    """Round a non-negative distance to the nearest integer, ties away from zero.

    Do not use Python's `round()`, which uses banker's rounding and can break
    matrix symmetry.
    """

    if value < 0:
        raise ValueError("distance rounding expects a non-negative value")
    return math.floor(value + 0.5)


def metres_to_display_km(metres: int) -> str:
    """Format stored metres as kilometres with three decimal places."""

    return f"{metres / 1000:.3f}"


def haversine_metres(lat_i: float, lon_i: float, lat_j: float, lon_j: float) -> float:
    """Great-circle distance in metres using the specification formula."""

    phi1 = math.radians(lat_i)
    phi2 = math.radians(lat_j)
    delta_phi = math.radians(lat_j - lat_i)
    delta_lambda = math.radians(lon_j - lon_i)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(
        delta_lambda / 2
    ) ** 2
    a = min(1.0, max(0.0, a))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_M * c


def integer_metres(haversine_m: float, detour_factor: Decimal) -> int:
    raw_metres = haversine_m * float(detour_factor)
    return round_half_up(raw_metres)


def ordered_node_ids(depot_id: str, customer_ids: list[str]) -> list[str]:
    """Depot first, then customers sorted lexicographically by id."""

    return [depot_id, *sorted(customer_ids)]


def matrix_lookup(matrix: DistanceMatrix, origin: str, destination: str) -> int:
    try:
        i = matrix.node_ids.index(origin)
        j = matrix.node_ids.index(destination)
    except ValueError as exc:
        raise KeyError(f"unknown matrix node: {origin!r} or {destination!r}") from exc
    return matrix.distances_metres[i][j]


def build_geographic_matrix(
    depot: Depot,
    customers: list[Customer],
    detour_factor: Decimal,
) -> DistanceMatrix:
    """Build a symmetric integer-metre matrix by computing one triangle and mirroring."""

    if depot.latitude is None or depot.longitude is None:
        raise ValueError("geographic matrix requires depot coordinates")
    coords: dict[str, tuple[float, float]] = {
        depot.depot_id: (depot.latitude, depot.longitude),
    }
    for customer in customers:
        if customer.latitude is None or customer.longitude is None:
            raise ValueError(f"geographic matrix requires coordinates for {customer.customer_id}")
        coords[customer.customer_id] = (customer.latitude, customer.longitude)

    node_ids = ordered_node_ids(depot.depot_id, [customer.customer_id for customer in customers])
    size = len(node_ids)
    distances = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(i + 1, size):
            lat_i, lon_i = coords[node_ids[i]]
            lat_j, lon_j = coords[node_ids[j]]
            metres = integer_metres(haversine_metres(lat_i, lon_i, lat_j, lon_j), detour_factor)
            distances[i][j] = metres
            distances[j][i] = metres
    return DistanceMatrix(node_ids=node_ids, distances_metres=distances)
