"""Reconstruct MILP symbols from returned routes for display only.

OR-Tools does not expose native three-index variables. Incoming/outgoing
counts and selected arcs are rebuilt from consecutive stop sequences.
Displayed loads are cumulative tote counts, not MTZ potentials w_ik.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from display import display_node, format_decimal, format_km, reconstructed_arcs, scenario_label

CHECK_LABEL_KEYS = {
    "DEMAND_SATISFACTION": "inspect.check.coverage",
    "CAPACITY": "inspect.check.capacity",
    "DEPOT_CONNECTIVITY": "inspect.check.depot",
    "DISTANCE": "inspect.check.distance",
    "INVARIANTS": "inspect.check.invariants",
}

CHECK_DETAIL_KEYS = {
    ("DEMAND_SATISFACTION", True): "inspect.check.coverage.ok",
    ("DEMAND_SATISFACTION", False): "inspect.check.coverage.fail",
    ("CAPACITY", True): "inspect.check.capacity.ok",
    ("CAPACITY", False): "inspect.check.capacity.fail",
    ("DEPOT_CONNECTIVITY", True): "inspect.check.depot.ok",
    ("DEPOT_CONNECTIVITY", False): "inspect.check.depot.fail",
    ("DISTANCE", True): "inspect.check.distance.ok",
    ("DISTANCE", False): "inspect.check.distance.fail",
    ("INVARIANTS", True): "inspect.check.invariants.ok",
}

NON_SUCCESS_STATUSES = {
    "heuristic_incomplete",
    "no_solution_found",
    "infeasible",
    "invalid",
    "error",
    "pending",
}


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
    from i18n import t

    incoming: Counter[str] = Counter()
    outgoing: Counter[str] = Counter()
    for arc in arcs:
        outgoing[arc["from_id"]] += 1
        incoming[arc["to_id"]] += 1
    rows = []
    for node_id in node_ids:
        rows.append(
            {
                t("inspect.cum.node"): display_node(node_id),
                t("inspect.col.outgoing"): outgoing[node_id],
                t("inspect.col.incoming"): incoming[node_id],
            }
        )
    return rows


def route_matrix(
    node_ids: list[str],
    sequence: list[str],
) -> list[dict[str, Any]]:
    from i18n import t

    selected = set(reconstructed_arcs(sequence))
    labels = [display_node(node_id) for node_id in node_ids]
    origin_label = t("inspect.col.from")
    rows = []
    for origin in node_ids:
        row: dict[str, Any] = {origin_label: display_node(origin)}
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


def outcome_label(passed: bool) -> str:
    from i18n import t

    return t("ux.plan.check.passed") if passed else t("ux.plan.check.failed")


def demand_check_label(value: str | None) -> str:
    from i18n import t

    token = str(value or "").strip().lower()
    if token == "pass":
        return t("ux.plan.check.passed")
    if token == "fail":
        return t("ux.plan.check.failed")
    return str(value or t("common.na"))


def check_name(check: dict[str, Any]) -> str:
    from i18n import t

    code = str(check.get("code") or "")
    key = CHECK_LABEL_KEYS.get(code)
    if key:
        return t(key)
    name = str(check.get("name") or code or t("common.na"))
    return name.replace("_", " ")


def check_explanation(check: dict[str, Any]) -> str:
    from i18n import t

    code = str(check.get("code") or "")
    passed = bool(check.get("passed"))
    key = CHECK_DETAIL_KEYS.get((code, passed))
    if key:
        return t(key)
    message = str(check.get("message") or "").replace("_", " ").strip()
    return message


def checks_passed_count(checks: list[dict[str, Any]]) -> tuple[int, int]:
    total = len(checks)
    passed = sum(1 for check in checks if check.get("passed"))
    return passed, total


def checks_all_passed(checks: list[dict[str, Any]]) -> bool:
    passed, total = checks_passed_count(checks)
    return total > 0 and passed == total


def verdict_copy(checks: list[dict[str, Any]]) -> tuple[bool, str]:
    from i18n import t

    if checks_all_passed(checks):
        return True, t("inspect.verdict.pass")
    return False, t("inspect.verdict.fail")


def is_optimised_run(run: dict[str, Any]) -> bool:
    return run.get("run_type") == "optimised"


def termination_label(value: str | None, *, optimised: bool) -> str:
    from i18n import t

    if not optimised or not value or value == "not_run":
        return t("common.na")
    key = f"inspect.term.{value}"
    label = t(key)
    if label == key:
        return str(value).replace("_", " ")
    return label


def seconds_label(value: Any, *, decimals: int | None = None) -> str:
    from i18n import t

    if value is None:
        return t("common.na")
    if decimals is None:
        display = str(int(value)) if float(value).is_integer() else format_decimal(float(value), 2)
    else:
        display = format_decimal(float(value), decimals)
    return t("inspect.meta.seconds", n=display)


def method_label(run: dict[str, Any]) -> str:
    from i18n import t

    if is_optimised_run(run):
        return t("ux.optimised")
    if run.get("run_type") == "baseline":
        return t("ux.baseline")
    return t("common.na")


def run_metadata_items(run: dict[str, Any]) -> list[tuple[str, str, str]]:
    from i18n import t

    optimised = is_optimised_run(run)
    scenario_id = str(run.get("scenario_id") or "")
    limit = run.get("solver_time_limit_seconds") if optimised else None
    runtime = run.get("solver_runtime_seconds") if optimised else None
    termination = run.get("solver_termination") if optimised else None
    return [
        (t("inspect.meta.scenario"), scenario_label(scenario_id), ""),
        (t("inspect.meta.method"), method_label(run), ""),
        (t("inspect.meta.termination"), termination_label(termination, optimised=optimised), ""),
        (t("inspect.meta.limit"), seconds_label(limit), ""),
        (t("inspect.meta.runtime"), seconds_label(runtime, decimals=2), ""),
        (
            t("inspect.meta.run_id"),
            str(run.get("run_id") or t("common.na")),
            "lm-inspect-runid",
        ),
    ]


def assignment_rows(assignments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from i18n import t

    rows = []
    for item in assignments:
        served = item["demand_totes"] if item["service_count"] == 1 else 0
        rows.append(
            {
                t("inspect.col.customer"): item["customer_id"],
                t("inspect.col.required"): item["demand_totes"],
                t("inspect.col.delivered"): served,
                t("inspect.col.vehicle"): item.get("assigned_vehicle") or t("common.na"),
                t("inspect.col.visits"): item["service_count"],
                t("inspect.col.check"): demand_check_label(item.get("demand_check")),
            }
        )
    return rows


def selected_leg_rows(arcs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from i18n import t

    return [
        {
            t("table.vehicle"): arc["vehicle_id"],
            t("inspect.col.from"): arc["from"],
            t("inspect.col.to"): arc["to"],
            t("inspect.col.selected"): arc["reconstructed_x"],
            t("inspect.col.leg"): arc["distance"],
        }
        for arc in arcs
    ]
