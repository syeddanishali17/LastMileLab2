"""Generate README schematic figures from live core plans.

Run from the project root:

    .\\.venv\\Scripts\\python.exe scripts\\generate_portfolio_figures.py

Figures are synthetic schematic connections, not road geometry.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.baseline import plan_baseline
from app.core.kpis import compute_scenario_kpis, metres_to_km
from app.core.loader import load_and_precheck
from app.core.optimizer import plan_optimise
from app.core.routes import node_sequence_for_vehicle

OUT = ROOT / "docs" / "screenshots"
VEHICLE_COLOURS = {
    "V01": (31, 78, 121),
    "V02": (46, 125, 79),
    "V03": (184, 92, 56),
    "V04": (107, 76, 154),
}
ZONE_COLOURS = {
    "Z1": (31, 78, 121),
    "Z2": (46, 125, 79),
    "Z3": (184, 92, 56),
    "Z4": (107, 76, 154),
}
LEARNING_POSITIONS = {
    "DEPOT_L6": (0.0, 0.0),
    "C1": (1.15, 0.55),
    "C2": (1.45, -0.35),
    "C3": (0.35, -1.15),
    "C4": (-0.95, -0.85),
    "C5": (-1.35, 0.15),
    "C6": (-0.55, 1.05),
}


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _project(
    lat: float, lon: float, bounds: tuple[float, float, float, float], box: tuple[int, int, int, int]
) -> tuple[int, int]:
    south, north, west, east = bounds
    left, top, right, bottom = box
    x = left + (lon - west) / (east - west) * (right - left)
    y = bottom - (lat - south) / (north - south) * (bottom - top)
    return int(round(x)), int(round(y))


def _geo_bounds(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    pad_lat = max((max(lats) - min(lats)) * 0.12, 0.012)
    pad_lon = max((max(lons) - min(lons)) * 0.12, 0.012)
    return min(lats) - pad_lat, max(lats) + pad_lat, min(lons) - pad_lon, max(lons) + pad_lon


def _draw_panel(
    draw: ImageDraw.ImageDraw,
    *,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    plan,
    dataset,
    fonts: dict[str, ImageFont.ImageFont],
) -> None:
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=18, fill=(248, 250, 252), outline=(210, 218, 228), width=2)
    draw.text((left + 22, top + 16), title, fill=(15, 39, 68), font=fonts["title"])
    draw.text((left + 22, top + 52), subtitle, fill=(70, 84, 102), font=fonts["small"])
    map_box = (left + 28, top + 86, right - 28, bottom - 58)
    draw.rounded_rectangle(map_box, radius=12, fill=(236, 242, 247), outline=(198, 210, 222))

    coords = {dataset.depot.depot_id: (dataset.depot.latitude, dataset.depot.longitude)}
    zones = {}
    for customer in dataset.customers:
        coords[customer.customer_id] = (customer.latitude, customer.longitude)
        zones[customer.customer_id] = customer.zone_id
    bounds = _geo_bounds(list(coords.values()))
    used = [route for route in plan.routes if route.is_used]
    for index, route in enumerate(used):
        sequence = node_sequence_for_vehicle(plan.stops, route.vehicle_id)
        colour = VEHICLE_COLOURS.get(route.vehicle_id, (44, 62, 80))
        points = [_project(*coords[node_id], bounds, map_box) for node_id in sequence]
        if len(points) >= 2:
            draw.line(points, fill=colour, width=5, joint="curve")
        label = f"{route.vehicle_id}  {route.assigned_demand_totes} totes  {metres_to_km(route.distance_metres):.3f} km"
        draw.text((left + 28 + index * 210, bottom - 42), label, fill=colour, font=fonts["tiny"])

    for customer in dataset.customers:
        x, y = _project(*coords[customer.customer_id], bounds, map_box)
        fill = ZONE_COLOURS.get(zones[customer.customer_id], (80, 80, 80))
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=fill, outline=(255, 255, 255), width=2)

    depot_xy = _project(*coords[dataset.depot.depot_id], bounds, map_box)
    dx, dy = depot_xy
    draw.ellipse((dx - 11, dy - 11, dx + 11, dy + 11), fill=(15, 39, 68), outline=(212, 160, 23), width=3)
    draw.text((dx + 14, dy - 12), "Depot", fill=(15, 39, 68), font=fonts["small"])


def _draw_learning(
    draw: ImageDraw.ImageDraw,
    *,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    sequences: dict[str, list[str]],
    unserved: list[str],
    fonts: dict[str, ImageFont.ImageFont],
) -> None:
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=18, fill=(248, 250, 252), outline=(210, 218, 228), width=2)
    draw.text((left + 20, top + 14), title, fill=(15, 39, 68), font=fonts["title"])
    draw.text((left + 20, top + 48), subtitle, fill=(70, 84, 102), font=fonts["small"])
    map_box = (left + 24, top + 82, right - 24, bottom - 20)
    xs = [p[0] for p in LEARNING_POSITIONS.values()]
    ys = [p[1] for p in LEARNING_POSITIONS.values()]
    pad = 0.35
    min_x, max_x = min(xs) - pad, max(xs) + pad
    min_y, max_y = min(ys) - pad, max(ys) + pad

    def to_xy(node_id: str) -> tuple[int, int]:
        px, py = LEARNING_POSITIONS[node_id]
        x = map_box[0] + (px - min_x) / (max_x - min_x) * (map_box[2] - map_box[0])
        y = map_box[3] - (py - min_y) / (max_y - min_y) * (map_box[3] - map_box[1])
        return int(round(x)), int(round(y))

    for vehicle_id, sequence in sequences.items():
        if len(sequence) < 3:
            continue
        colour = VEHICLE_COLOURS.get(vehicle_id, (44, 62, 80))
        points = [to_xy(node_id) for node_id in sequence]
        draw.line(points, fill=colour, width=5, joint="curve")

    for node_id in LEARNING_POSITIONS:
        x, y = to_xy(node_id)
        if node_id.startswith("DEPOT"):
            draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(15, 39, 68), outline=(212, 160, 23), width=3)
            draw.text((x + 16, y - 10), "Depot", fill=(15, 39, 68), font=fonts["small"])
            continue
        fill = (185, 48, 48) if node_id in unserved else (31, 78, 121)
        draw.ellipse((x - 11, y - 11, x + 11, y + 11), fill=fill, outline=(255, 255, 255), width=2)
        draw.text((x - 10, y + 14), node_id, fill=(15, 39, 68), font=fonts["tiny"])


def _write_architecture_svg(path: Path) -> None:
    path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640">
  <rect width="1280" height="640" fill="#f6f8fb"/>
  <text x="48" y="48" font-family="Segoe UI, Arial, sans-serif" font-size="28" fill="#0f2744">LastMile Lab architecture</text>
  <text x="48" y="80" font-family="Segoe UI, Arial, sans-serif" font-size="16" fill="#465466">Streamlit never solves. FastAPI never owns KPI formulae. Core is testable without either process.</text>
  <rect x="48" y="120" width="240" height="120" rx="16" fill="#0f2744"/>
  <text x="168" y="172" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="18" fill="#d4a017">Streamlit UI</text>
  <text x="168" y="198" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#e8eef4">port 8501</text>
  <rect x="368" y="120" width="240" height="120" rx="16" fill="#1f4e79"/>
  <text x="488" y="172" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="18" fill="#ffffff">FastAPI /api/v1</text>
  <text x="488" y="198" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#d9e6f2">port 8000</text>
  <rect x="688" y="88" width="544" height="184" rx="16" fill="#ffffff" stroke="#c6d0dc"/>
  <text x="960" y="124" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="18" fill="#0f2744">backend/app/core</text>
  <rect x="716" y="148" width="150" height="88" rx="12" fill="#2e7d4f"/>
  <text x="791" y="188" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="14" fill="#ffffff">Validation</text>
  <text x="791" y="208" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#e7f5ec">matrix / checks</text>
  <rect x="884" y="148" width="150" height="88" rx="12" fill="#b85c38"/>
  <text x="959" y="188" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="14" fill="#ffffff">NN baseline</text>
  <text x="959" y="208" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#f8ece6">sequential</text>
  <rect x="1052" y="148" width="150" height="88" rx="12" fill="#6b4c9a"/>
  <text x="1127" y="188" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="14" fill="#ffffff">OR-Tools</text>
  <text x="1127" y="208" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#f3edf8">RoutingModel</text>
  <rect x="368" y="360" width="544" height="120" rx="16" fill="#ffffff" stroke="#c6d0dc"/>
  <text x="640" y="412" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="18" fill="#0f2744">DuckDB run history</text>
  <text x="640" y="440" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#465466">data/runs/lastmile.duckdb  ·  JSON and CSV export</text>
  <rect x="48" y="360" width="240" height="120" rx="16" fill="#ffffff" stroke="#c6d0dc"/>
  <text x="168" y="412" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="18" fill="#0f2744">Pytest</text>
  <text x="168" y="440" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#465466">calls core directly</text>
  <path d="M288 180 H368" stroke="#0f2744" stroke-width="3" fill="none" marker-end="url(#arrow)"/>
  <path d="M608 180 H688" stroke="#0f2744" stroke-width="3" fill="none"/>
  <path d="M488 240 V360" stroke="#0f2744" stroke-width="3" fill="none"/>
  <path d="M168 280 V360" stroke="#0f2744" stroke-width="3" fill="none"/>
  <text x="48" y="560" font-family="Segoe UI, Arial, sans-serif" font-size="14" fill="#465466">OR-Tools does not solve the documented three-index MILP. The inspector reconstructs x, y, u and cumulative tote loads from returned routes.</text>
  <text x="48" y="584" font-family="Segoe UI, Arial, sans-serif" font-size="14" fill="#465466">Displayed kilometres are synthetic Haversine estimates, not live Vienna road distances.</text>
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 z" fill="#0f2744"/>
    </marker>
  </defs>
</svg>
""",
        encoding="utf-8",
    )


def _plan_rows(plan) -> list[dict[str, object]]:
    rows = []
    for route in plan.routes:
        rows.append(
            {
                "vehicle_id": route.vehicle_id,
                "is_used": route.is_used,
                "assigned_demand_totes": route.assigned_demand_totes,
                "distance_metres": int(route.distance_metres),
                "sequence": node_sequence_for_vehicle(plan.stops, route.vehicle_id),
            }
        )
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fonts = {
        "hero": _font(34),
        "title": _font(22),
        "small": _font(15),
        "tiny": _font(13),
        "caption": _font(14),
    }

    _, vienna = load_and_precheck("VIENNA_STANDARD_24")
    baseline = plan_baseline("VIENNA_STANDARD_24")
    optimised = plan_optimise("VIENNA_STANDARD_24", time_limit_seconds=5)
    kpis = compute_scenario_kpis(vienna, optimised, baseline_plan=baseline)

    hero = Image.new("RGB", (1600, 900), (246, 248, 251))
    draw = ImageDraw.Draw(hero)
    draw.text((48, 28), "Vienna Standard 24  ·  schematic synthetic connections", fill=(15, 39, 68), font=fonts["hero"])
    nn_km = metres_to_km(baseline.run.objective_distance_metres)
    opt_km = metres_to_km(optimised.run.objective_distance_metres)
    improvement = kpis.distance_improvement_percentage
    _draw_panel(
        draw,
        box=(40, 90, 780, 820),
        title="Nearest-neighbour baseline",
        subtitle=f"Complete feasible plan  ·  {nn_km:.3f} km  ·  4 vans  ·  loads 29 / 28 / 29 / 22",
        plan=baseline,
        dataset=vienna,
        fonts=fonts,
    )
    _draw_panel(
        draw,
        box=(820, 90, 1560, 820),
        title="OR-Tools  ·  5 s  ·  9.11.4210",
        subtitle=(
            f"Best feasible within search limit  ·  {opt_km:.3f} km  ·  "
            f"improvement {improvement:.1f}%"
        ),
        plan=optimised,
        dataset=vienna,
        fonts=fonts,
    )
    draw.text(
        (48, 848),
        "Not road geometry or live traffic. Depot is navy with a gold ring. Customer dots are coloured by zone.",
        fill=(70, 84, 102),
        font=fonts["caption"],
    )
    hero.save(OUT / "hero_vienna_standard_24.png")

    nn_only = Image.new("RGB", (960, 720), (246, 248, 251))
    nn_draw = ImageDraw.Draw(nn_only)
    _draw_panel(
        nn_draw,
        box=(24, 24, 936, 696),
        title="Vienna Standard 24 baseline",
        subtitle=f"Sequential nearest neighbour  ·  {nn_km:.3f} km  ·  comparison-eligible",
        plan=baseline,
        dataset=vienna,
        fonts=fonts,
    )
    nn_only.save(OUT / "vienna_baseline_schematic.png")

    opt_only = Image.new("RGB", (960, 720), (246, 248, 251))
    opt_draw = ImageDraw.Draw(opt_only)
    _draw_panel(
        opt_draw,
        box=(24, 24, 936, 696),
        title="Vienna Standard 24 OR-Tools",
        subtitle=f"PATH_CHEAPEST_ARC + GUIDED_LOCAL_SEARCH  ·  5 s  ·  {opt_km:.3f} km",
        plan=optimised,
        dataset=vienna,
        fonts=fonts,
    )
    opt_only.save(OUT / "vienna_optimised_schematic.png")

    learning_nn = plan_baseline("LEARNING_6")
    learning_opt = plan_optimise("LEARNING_6", time_limit_seconds=5)
    lab = Image.new("RGB", (1600, 620), (246, 248, 251))
    lab_draw = ImageDraw.Draw(lab)
    lab_draw.text((48, 24), "LEARNING_6  ·  teaching diagram, not a map", fill=(15, 39, 68), font=fonts["hero"])
    _draw_learning(
        lab_draw,
        box=(40, 90, 520, 580),
        title="Sequential NN",
        subtitle="heuristic_incomplete  ·  C4 unserved  ·  27.000 km partial",
        sequences={
            route.vehicle_id: node_sequence_for_vehicle(learning_nn.stops, route.vehicle_id)
            for route in learning_nn.routes
            if route.is_used
        },
        unserved=learning_nn.run.unserved_customer_ids,
        fonts=fonts,
    )
    _draw_learning(
        lab_draw,
        box=(540, 90, 1020, 580),
        title="Named packing 34.000 km",
        subtitle="Teaching comparison  ·  not sequential NN",
        sequences={
            "V01": ["DEPOT_L6", "C1", "C2", "C6", "DEPOT_L6"],
            "V02": ["DEPOT_L6", "C5", "C4", "C3", "DEPOT_L6"],
        },
        unserved=[],
        fonts=fonts,
    )
    _draw_learning(
        lab_draw,
        box=(1040, 90, 1560, 580),
        title="Verified optimum 31.000 km",
        subtitle="Enumerated  ·  OR-Tools matches 31000 m",
        sequences={
            route.vehicle_id: node_sequence_for_vehicle(learning_opt.stops, route.vehicle_id)
            for route in learning_opt.routes
            if route.is_used
        },
        unserved=[],
        fonts=fonts,
    )
    lab.save(OUT / "learning_6_teaching.png")

    _write_architecture_svg(OUT / "architecture.svg")

    payload = {
        "scenario_id": "VIENNA_STANDARD_24",
        "computed_at": "2026-09-04",
        "ortools_version": "9.11.4210",
        "solver_time_limit_seconds": 5,
        "first_solution_strategy": "PATH_CHEAPEST_ARC",
        "local_search": "GUIDED_LOCAL_SEARCH",
        "baseline": {
            "status": baseline.run.status.value,
            "comparison_eligible": baseline.run.comparison_eligible,
            "objective_distance_metres": baseline.run.objective_distance_metres,
            "objective_distance_km": nn_km,
            "vehicles_used": baseline.run.vehicles_used,
            "routes": _plan_rows(baseline),
        },
        "optimised": {
            "status": optimised.run.status.value,
            "comparison_eligible": optimised.run.comparison_eligible,
            "solver_termination": (
                optimised.run.solver_termination.value
                if optimised.run.solver_termination
                else None
            ),
            "objective_distance_metres": optimised.run.objective_distance_metres,
            "objective_distance_km": opt_km,
            "vehicles_used": optimised.run.vehicles_used,
            "solver_runtime_seconds": (
                float(optimised.run.solver_runtime_seconds)
                if optimised.run.solver_runtime_seconds is not None
                else None
            ),
            "routes": _plan_rows(optimised),
        },
        "distance_improvement_percentage": float(improvement) if improvement is not None else None,
        "distance_improvement_display": f"{improvement:.1f}%",
        "total_demand_totes": 108,
        "total_fleet_capacity_totes": 120,
        "used_fleet_utilisation": (
            float(kpis.used_fleet_utilisation)
            if kpis.used_fleet_utilisation is not None
            else None
        ),
        "note": (
            "Ordinary OR-Tools output is the best feasible plan found within the "
            "search limit. It is not globally optimal. Guided local search is not "
            "bit-deterministic; re-runs may differ slightly."
        ),
    }
    (OUT / "vienna_standard_24_publish.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({
        "nn_km": nn_km,
        "opt_km": opt_km,
        "improvement": improvement,
        "opt_metres": optimised.run.objective_distance_metres,
    }))


if __name__ == "__main__":
    main()
