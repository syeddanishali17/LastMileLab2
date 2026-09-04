"""Display helpers. These format API values; they do not solve routes or KPIs."""

from __future__ import annotations

from typing import Any

VEHICLE_COLOURS = [
    "#1f4e79",
    "#2e7d4f",
    "#b85c38",
    "#6b4c9a",
    "#0f7a8c",
    "#8a1c3c",
    "#5c4a32",
    "#3d5a40",
    "#7a5c00",
    "#2c3e50",
]

MAP_CAPTION = (
    "Schematic connections based on synthetic estimated distances. "
    "These lines are not road geometry or live driving directions."
)
SYNTHETIC_NOTICE = (
    "LastMile Lab is a fictional portfolio case study. ViennaCart is a fictional "
    "operator. All depots, customers, order demands, routes, distances, and "
    "operating assumptions are synthetic. The application does not use proprietary "
    "customer data or live Vienna traffic information."
)


def vehicle_colour(vehicle_id: str) -> str:
    index = 0
    digits = "".join(char for char in vehicle_id if char.isdigit())
    if digits:
        index = max(int(digits) - 1, 0)
    return VEHICLE_COLOURS[index % len(VEHICLE_COLOURS)]


def display_node(node_id: str) -> str:
    if node_id.startswith("DEPOT"):
        return "Depot"
    return node_id


def format_km(metres: int | float | None) -> str:
    if metres is None:
        return "—"
    return f"{float(metres) / 1000:.3f} km"


def format_km_value(km: float | None) -> str:
    if km is None:
        return "—"
    return f"{float(km):.3f} km"


def format_pct(fraction: float | None) -> str:
    if fraction is None:
        return "—"
    return f"{float(fraction) * 100:.1f}%"


def format_sequence(node_ids: list[str]) -> str:
    return " -> ".join(display_node(node_id) for node_id in node_ids)


def matrix_lookup(matrix: dict[str, Any], origin: str, destination: str) -> int:
    node_ids: list[str] = matrix["node_ids"]
    distances: list[list[int]] = matrix["distances_metres"]
    return distances[node_ids.index(origin)][node_ids.index(destination)]


def path_distance_metres(matrix: dict[str, Any], sequence: list[str]) -> int:
    total = 0
    for index in range(len(sequence) - 1):
        total += matrix_lookup(matrix, sequence[index], sequence[index + 1])
    return total


def reconstructed_arcs(sequence: list[str]) -> list[tuple[str, str]]:
    return list(zip(sequence, sequence[1:], strict=False))


def incomplete_baseline_note(summary: dict[str, Any]) -> str | None:
    if summary.get("status") != "heuristic_incomplete":
        return None
    unserved = ", ".join(summary.get("unserved_customer_ids") or [])
    if summary.get("scenario_id") == "LEARNING_6":
        return (
            "This is the expected LEARNING_6 nearest-neighbour result, not a failed run. "
            f"Sequential construction leaves {unserved or 'C4'} unserved, so total distance "
            "stays empty and the kilometres shown are a partial plan only. "
            "This is not the 34.000 km teaching packing. Run OR-Tools on LEARNING_6 "
            "for the 31.000 km complete plan, or open Learning Lab."
        )
    return (
        "Nearest neighbour built some routes but could not serve every customer. "
        "The plan is not comparison-eligible."
        + (f" Unserved: {unserved}." if unserved else "")
    )


def format_improvement(percentage: float | None) -> str:
    if percentage is None:
        return "—"
    return f"{float(percentage):.1f}%"


def matrix_km_rows(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    node_ids: list[str] = matrix["node_ids"]
    distances: list[list[int]] = matrix["distances_metres"]
    labels = [display_node(node_id) for node_id in node_ids]
    rows: list[dict[str, Any]] = []
    for origin, row_metres in zip(node_ids, distances, strict=True):
        row: dict[str, Any] = {"from": display_node(origin)}
        for label, metres in zip(labels, row_metres, strict=True):
            row[label] = f"{metres / 1000:.3f}"
        rows.append(row)
    return rows


def operational_summary(baseline: dict[str, Any], optimised: dict[str, Any]) -> str:
    baseline_status = baseline.get("status")
    optimised_status = optimised.get("status")
    if not baseline.get("comparison_eligible"):
        unserved = baseline.get("unserved_customer_ids") or []
        parts = [
            f"The baseline is `{baseline_status}` and is not comparison-eligible, "
            "so no distance-improvement percentage is shown."
        ]
        if unserved:
            parts.append("Unserved customers: " + ", ".join(unserved) + ".")
        partial = baseline.get("partial_distance_metres")
        if partial is not None:
            parts.append(
                "The constructed baseline routes cover "
                f"{format_km(partial)} as a partial plan only."
            )
        if optimised.get("comparison_eligible"):
            parts.append(
                "The optimiser returned a complete plan of "
                f"{format_km(optimised.get('objective_distance_metres'))}."
            )
        else:
            parts.append(f"The optimiser status is `{optimised_status}`.")
        return " ".join(parts)

    if not optimised.get("comparison_eligible"):
        return (
            f"The baseline is complete at {format_km(baseline.get('objective_distance_metres'))}, "
            f"but the optimiser is `{optimised_status}` and cannot be compared on total distance."
        )

    baseline_km = format_km(baseline.get("objective_distance_metres"))
    optimised_km = format_km(optimised.get("objective_distance_metres"))
    improvement = optimised.get("distance_improvement_percentage")
    return (
        f"The nearest-neighbour baseline covers {baseline_km} "
        f"with {baseline.get('vehicles_used')} vans. OR-Tools returns "
        f"{optimised_km} using "
        f"{optimised.get('vehicles_used')} vans. Distance improvement: "
        f"{format_improvement(improvement)}."
    )


REFERENCE_PACKING_34KM = {
    "label": "34.000 km reference packing",
    "note": (
        "Teaching comparison only. This is a named feasible packing, not the "
        "sequential nearest-neighbour output and not an OR-Tools run."
    ),
    "routes": [
        {
            "vehicle_id": "V01",
            "pack": ["C1", "C2", "C6"],
            "sequence": ["DEPOT_L6", "C1", "C2", "C6", "DEPOT_L6"],
        },
        {
            "vehicle_id": "V02",
            "pack": ["C5", "C4", "C3"],
            "sequence": ["DEPOT_L6", "C5", "C4", "C3", "DEPOT_L6"],
        },
    ],
}


def packing_from_matrix(
    matrix: dict[str, Any],
    customers: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    demand = {
        customer["customer_id"]: customer["demand_totes"]
        for customer in customers or []
    }
    routes = []
    total = 0
    for route in REFERENCE_PACKING_34KM["routes"]:
        metres = path_distance_metres(matrix, route["sequence"])
        total += metres
        load = sum(demand.get(customer_id, 0) for customer_id in route["pack"])
        routes.append({**route, "distance_metres": metres, "load_totes": load})
    return {
        "label": REFERENCE_PACKING_34KM["label"],
        "note": REFERENCE_PACKING_34KM["note"],
        "total_distance_metres": total,
        "routes": routes,
    }
