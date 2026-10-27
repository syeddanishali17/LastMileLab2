"""Continuum-approximation (CA) estimate of total fleet distance, before any solving.

Daganzo (1984) showed that the length of capacitated delivery tours in a service
area is well approximated by a line-haul term plus a local-tour term:

    L ≈ 2 · r̄ · m  +  k · √(n · A)

with n customers in an area A, mean depot-to-customer distance r̄, m = ⌈demand / Q⌉
routes and k ≈ 0.57. Merchán & Winkenbach (MIT CTL; Networks, 2019) validated CA
on real urban road networks and showed it must be scaled by the network's circuity
(road distance / straight-line distance), which is measured here from the scenario's
own distance matrix. This is an estimate for planning conversations, not a bound.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Any

DAGANZO_K = 0.57
EARTH_RADIUS_KM = 6371.0088
KM_PER_DEG_LAT = 110.574
KM_PER_DEG_LON_EQUATOR = 111.320
# Pairs closer than this are dominated by rounding in the integer-metre matrix.
MIN_PAIR_KM = 0.05


@dataclass(frozen=True)
class ContinuumEstimate:
    customers: int
    area_km2: float
    mean_linehaul_km: float
    routes: int
    circuity: float
    k: float

    @property
    def linehaul_km(self) -> float:
        return self.circuity * 2 * self.mean_linehaul_km * self.routes

    @property
    def local_km(self) -> float:
        return self.circuity * self.k * math.sqrt(self.customers * self.area_km2)

    @property
    def total_km(self) -> float:
        return self.linehaul_km + self.local_km


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(h))


def convex_hull_area_km2(points: list[tuple[float, float]]) -> float:
    """Area of the convex hull of (lat, lon) points on a local flat projection."""
    if len(points) < 3:
        return 0.0
    lat0 = math.radians(statistics.fmean(lat for lat, _ in points))
    plane = sorted(
        {
            (lon * KM_PER_DEG_LON_EQUATOR * math.cos(lat0), lat * KM_PER_DEG_LAT)
            for lat, lon in points
        }
    )
    if len(plane) < 3:
        return 0.0

    def cross(o: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[tuple[float, float]] = []
    upper: list[tuple[float, float]] = []
    for point in plane:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    for point in reversed(plane):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    hull = lower[:-1] + upper[:-1]
    twice_area = sum(
        hull[i][0] * hull[(i + 1) % len(hull)][1] - hull[(i + 1) % len(hull)][0] * hull[i][1]
        for i in range(len(hull))
    )
    return abs(twice_area) / 2


def measured_circuity(payload: dict[str, Any], coords: dict[str, tuple[float, float]]) -> float:
    """Median ratio of matrix (road-like) distance to straight-line distance."""
    matrix = payload.get("distance_matrix") or {}
    node_ids = matrix.get("node_ids") or []
    rows = matrix.get("distances_metres") or []
    ratios = []
    for i, origin in enumerate(node_ids):
        for j in range(i + 1, len(node_ids)):
            destination = node_ids[j]
            if origin not in coords or destination not in coords:
                continue
            straight = haversine_km(coords[origin], coords[destination])
            if straight >= MIN_PAIR_KM:
                ratios.append(rows[i][j] / 1000 / straight)
    return statistics.median(ratios) if ratios else 1.0


def estimate(payload: dict[str, Any] | None, *, k: float = DAGANZO_K) -> ContinuumEstimate | None:
    """CA estimate for a scenario payload, or None when it has no usable coordinates."""
    if not isinstance(payload, dict):
        return None
    scenario = payload.get("scenario") or {}
    depot = payload.get("depot") or {}
    customers = payload.get("customers") or []
    capacity = int(scenario.get("vehicle_capacity_totes") or 0)
    if not scenario.get("has_geographic_coordinates", True) or not customers or capacity <= 0:
        return None
    try:
        depot_point = (float(depot["latitude"]), float(depot["longitude"]))
        points = [(float(c["latitude"]), float(c["longitude"])) for c in customers]
    except (KeyError, TypeError, ValueError):
        return None
    coords = {str(depot.get("depot_id")): depot_point}
    coords.update({str(c["customer_id"]): point for c, point in zip(customers, points)})
    demand = sum(int(c.get("demand_totes") or 0) for c in customers)
    return ContinuumEstimate(
        customers=len(points),
        area_km2=convex_hull_area_km2(points),
        mean_linehaul_km=statistics.fmean(haversine_km(depot_point, p) for p in points),
        routes=max(1, math.ceil(demand / capacity)),
        circuity=measured_circuity(payload, coords),
        k=k,
    )


def gap_pct(actual_km: float, estimate_km: float) -> float:
    """Signed gap of an actual plan against the estimate, in percent."""
    return 100 * (actual_km - estimate_km) / estimate_km if estimate_km else 0.0
