"""Route attractiveness: would a dispatcher accept this plan as drawn?

Distance is not the only thing planners judge. The routing literature measures how
"visually attractive" a plan is (Rossit, Vigo, Tohmé & Frutos, Computers &
Operations Research, 2019): compact routes, territories that do not overlap, and
few crossing arcs (Poot, Kant & Wagelmans, 2002). The Amazon Last Mile Routing
Research Challenge (MIT CTL, 2021) adds a driver-side view: real routes finish one
delivery zone before starting the next. These read-outs score returned plans on
those criteria; the solver does not optimise them.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from itertools import combinations
from typing import Any

from continuum import KM_PER_DEG_LAT, KM_PER_DEG_LON_EQUATOR

Point = tuple[float, float]


@dataclass(frozen=True)
class RouteQuality:
    crossings: int
    overlap_pct: float
    compactness_km: float
    zone_switches: int
    territories: dict[str, list[tuple[float, float]]]  # vehicle -> hull as (lat, lon)


def _projector(lat0: float):
    cos0 = math.cos(math.radians(lat0))

    def to_plane(lat: float, lon: float) -> Point:
        return (lon * KM_PER_DEG_LON_EQUATOR * cos0, lat * KM_PER_DEG_LAT)

    def to_geo(point: Point) -> tuple[float, float]:
        return (point[1] / KM_PER_DEG_LAT, point[0] / (KM_PER_DEG_LON_EQUATOR * cos0))

    return to_plane, to_geo


def _cross(o: Point, a: Point, b: Point) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def segments_cross(p1: Point, p2: Point, q1: Point, q2: Point) -> bool:
    """Proper intersection only: touching endpoints or collinear overlap do not count."""
    d1, d2 = _cross(q1, q2, p1), _cross(q1, q2, p2)
    d3, d4 = _cross(p1, p2, q1), _cross(p1, p2, q2)
    return d1 * d2 < 0 and d3 * d4 < 0


def convex_hull(points: list[Point]) -> list[Point]:
    """Counter-clockwise hull (Andrew's monotone chain)."""
    unique = sorted(set(points))
    if len(unique) < 3:
        return unique
    lower: list[Point] = []
    upper: list[Point] = []
    for point in unique:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    for point in reversed(unique):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def polygon_area(polygon: list[Point]) -> float:
    if len(polygon) < 3:
        return 0.0
    return abs(
        sum(
            polygon[i][0] * polygon[(i + 1) % len(polygon)][1]
            - polygon[(i + 1) % len(polygon)][0] * polygon[i][1]
            for i in range(len(polygon))
        )
    ) / 2


def clip_convex(subject: list[Point], clip: list[Point]) -> list[Point]:
    """Sutherland-Hodgman intersection of two counter-clockwise convex polygons."""
    output = subject
    for i in range(len(clip)):
        if not output:
            break
        a, b = clip[i], clip[(i + 1) % len(clip)]
        incoming, output = output, []
        for j in range(len(incoming)):
            current, previous = incoming[j], incoming[j - 1]
            current_in = _cross(a, b, current) >= 0
            previous_in = _cross(a, b, previous) >= 0
            if current_in != previous_in:
                output.append(_line_intersection(previous, current, a, b))
            if current_in:
                output.append(current)
    return output


def _line_intersection(p1: Point, p2: Point, q1: Point, q2: Point) -> Point:
    denominator = (p1[0] - p2[0]) * (q1[1] - q2[1]) - (p1[1] - p2[1]) * (q1[0] - q2[0])
    if denominator == 0:
        return p2
    t = ((p1[0] - q1[0]) * (q1[1] - q2[1]) - (p1[1] - q1[1]) * (q1[0] - q2[0])) / denominator
    return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))


def assess(scenario: dict[str, Any] | None, routes: dict[str, Any] | None) -> RouteQuality | None:
    """Score a returned plan, or None when coordinates or routes are missing."""
    if not isinstance(scenario, dict) or not isinstance(routes, dict):
        return None
    depot = scenario.get("depot") or {}
    customers = {c["customer_id"]: c for c in scenario.get("customers") or []}
    try:
        geo = {str(depot["depot_id"]): (float(depot["latitude"]), float(depot["longitude"]))}
        geo.update(
            {cid: (float(c["latitude"]), float(c["longitude"])) for cid, c in customers.items()}
        )
    except (KeyError, TypeError, ValueError):
        return None
    to_plane, to_geo = _projector(statistics.fmean(lat for lat, _ in geo.values()))
    plane = {node: to_plane(*coords) for node, coords in geo.items()}

    arcs: list[tuple[str, str, str]] = []  # (vehicle, from, to)
    hulls: dict[str, list[Point]] = {}
    spreads: list[float] = []
    zone_switches = 0
    for vehicle in routes.get("vehicle_kpis") or []:
        sequence = [node for node in vehicle.get("sequence") or [] if node in plane]
        stops = [node for node in sequence if node in customers]
        if not vehicle.get("is_used") or not stops:
            continue
        vehicle_id = vehicle["vehicle_id"]
        arcs.extend((vehicle_id, a, b) for a, b in zip(sequence, sequence[1:]) if a != b)
        points = [plane[node] for node in stops]
        centre = (statistics.fmean(x for x, _ in points), statistics.fmean(y for _, y in points))
        spreads.extend(math.dist(point, centre) for point in points)
        hulls[vehicle_id] = convex_hull(points)
        zones = [customers[node].get("zone_id") for node in stops]
        zone_switches += sum(1 for a, b in zip(zones, zones[1:]) if a and b and a != b)
    if not arcs:
        return None

    crossings = sum(
        1
        for (_, a1, a2), (_, b1, b2) in combinations(arcs, 2)
        if not {a1, a2} & {b1, b2}
        and segments_cross(plane[a1], plane[a2], plane[b1], plane[b2])
    )
    total_area = sum(polygon_area(hull) for hull in hulls.values())
    shared = sum(
        polygon_area(clip_convex(hulls[a], hulls[b]))
        for a, b in combinations(sorted(hulls), 2)
        if len(hulls[a]) >= 3 and len(hulls[b]) >= 3
    )
    return RouteQuality(
        crossings=crossings,
        overlap_pct=100 * shared / total_area if total_area else 0.0,
        compactness_km=statistics.fmean(spreads) if spreads else 0.0,
        zone_switches=zone_switches,
        territories={vehicle: [to_geo(p) for p in hull] for vehicle, hull in hulls.items()},
    )
