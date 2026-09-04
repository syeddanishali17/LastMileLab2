"""Reconstruct MILP symbols from returned routes for display only.

OR-Tools does not expose native three-index variables. Incoming/outgoing
counts and selected arcs are rebuilt from consecutive stop sequences.
Displayed loads are cumulative tote counts, not MTZ potentials w_ik.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from display import display_node, format_km, reconstructed_arcs


def selected_arcs(vehicle_kpis: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for vehicle in vehicle_kpis:
        if not vehicle.get("is_used"):
            continue
        sequence = vehicle.get("sequence") or []
        for origin, destination in reconstructed_arcs(sequence):
            rows.append(
                {
                    "vehicle_id": vehicle["vehicle_id"],
                    "from": display_node(origin),
                    "to": display_node(destination),
                    "from_id": origin,
                    "to_id": destination,
                    "reconstructed_x": 1,
                }
            )
    return rows


def attach_leg_distances(
    arcs: list[dict[str, Any]],
    stops: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_vehicle: dict[str, list[dict[str, Any]]] = {}
    for stop in stops:
        by_vehicle.setdefault(stop["vehicle_id"], []).append(stop)
    lookup: dict[tuple[str, str, str], int] = {}
    for vehicle_id, vehicle_stops in by_vehicle.items():
        ordered = sorted(vehicle_stops, key=lambda item: item["sequence_number"])
        for previous, current in zip(ordered, ordered[1:], strict=False):
            lookup[(vehicle_id, previous["node_id"], current["node_id"])] = current[
                "leg_distance_metres"
            ]
    for arc in arcs:
        metres = lookup.get((arc["vehicle_id"], arc["from_id"], arc["to_id"]))
        arc["leg_distance_metres"] = metres
        arc["distance"] = format_km(metres)
    return arcs


def incoming_outgoing(arcs: list[dict[str, Any]], node_ids: list[str]) -> list[dict[str, Any]]:
    incoming: Counter[str] = Counter()
    outgoing: Counter[str] = Counter()
    for arc in arcs:
        outgoing[arc["from_id"]] += 1
        incoming[arc["to_id"]] += 1
    rows = []
    for node_id in node_ids:
        rows.append(
            {
                "node": display_node(node_id),
                "outgoing reconstructed arcs": outgoing[node_id],
                "incoming reconstructed arcs": incoming[node_id],
            }
        )
    return rows


def route_matrix(
    node_ids: list[str],
    sequence: list[str],
) -> list[dict[str, Any]]:
    selected = set(reconstructed_arcs(sequence))
    labels = [display_node(node_id) for node_id in node_ids]
    rows = []
    for origin in node_ids:
        row: dict[str, Any] = {"from": display_node(origin)}
        for destination, label in zip(node_ids, labels, strict=True):
            row[label] = 1 if (origin, destination) in selected else 0
        rows.append(row)
    return rows


def cumulative_loads(stops: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from i18n import t

    rows = []
    for stop in sorted(stops, key=lambda item: (item["vehicle_id"], item["sequence_number"])):
        rows.append(
            {
                t("table.vehicle"): stop["vehicle_id"],
                t("inspect.cum.sequence"): stop["sequence_number"],
                t("inspect.cum.node"): display_node(stop["node_id"]),
                t("inspect.cum.demand"): stop["demand_totes"],
                t("inspect.cum.served"): stop["load_after_service_totes"],
                t("inspect.col.leg"): format_km(stop.get("leg_distance_metres")),
            }
        )
    return rows
