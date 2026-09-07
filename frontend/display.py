"""Display helpers. These format API values; they do not solve routes or KPIs."""

from __future__ import annotations

from typing import Any

VEHICLE_COLOURS = [
    "#2563EB",
    "#EA580C",
    "#7C3AED",
    "#C026D3",
    "#0891B2",
    "#CA8A04",
    "#0F766E",
    "#B42318",
    "#4F46E5",
    "#64748B",
]


def format_decimal(value: int | float, decimals: int) -> str:
    from i18n import current_language

    formatted = f"{float(value):.{decimals}f}"
    return formatted.replace(".", ",") if current_language() == "de" else formatted


def scenario_label(scenario_id: str) -> str:
    from i18n import t

    if scenario_id.startswith("GEN_"):
        return t("scenario.generated.label")
    key = f"scenario.{scenario_id}.label"
    label = t(key)
    if label == key:
        return scenario_id
    return label


def scenario_help(scenario_id: str) -> str:
    from i18n import t

    key = f"scenario.{scenario_id}.help"
    text = t(key)
    if text != key:
        return text
    if scenario_id.startswith("GEN_"):
        return t("scenario.generated.help")
    return t("scenario.fallback.help")


def scenario_caption(scenario_id: str) -> str:
    from i18n import t

    meta_key = f"scenario.{scenario_id}.meta"
    meta = t(meta_key)
    help_text = scenario_help(scenario_id)
    if meta == meta_key:
        return help_text
    return f"{meta}\n\n{help_text}"


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
        from i18n import t

        return t("common.na")
    return f"{format_decimal(float(metres) / 1000, 3)} km"


def format_km_value(km: float | None) -> str:
    if km is None:
        from i18n import t

        return t("common.na")
    return f"{format_decimal(float(km), 3)} km"


def format_pct(fraction: float | None) -> str:
    if fraction is None:
        from i18n import t

        return t("common.na")
    value = format_decimal(float(fraction) * 100, 1)
    from i18n import current_language

    return f"{value} %" if current_language() == "de" else f"{value}%"


def format_sequence(node_ids: list[str]) -> str:
    return " → ".join(display_node(node_id) for node_id in node_ids)


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
    from i18n import t

    if summary.get("status") != "heuristic_incomplete":
        return None
    unserved = ", ".join(summary.get("unserved_customer_ids") or [])
    if summary.get("scenario_id") == "LEARNING_6":
        return t("note.learning", unserved=unserved or "C4")
    extra = t("note.unserved", ids=unserved) if unserved else ""
    return t("note.incomplete", unserved=extra)


def status_label(status: str | None) -> str:
    from i18n import t

    if not status:
        return t("status.none")
    key = f"status.{status}.label"
    label = t(key)
    if label == key:
        return status.replace("_", " ")
    return label


def distance_source_label(source: str | None) -> str:
    from i18n import t

    if not source:
        return t("common.na")
    key = f"dist.{source}"
    label = t(key)
    return source if label == key else label


def humanize_check_message(check: dict[str, Any]) -> str:
    from i18n import t

    code = check.get("code")
    message = str(check.get("message") or "")
    passed = bool(check.get("passed"))
    if code == "CHECK_4" and passed:
        return t("check.msg.integrity_ok")
    if code == "CHECK_1":
        return t("check.msg.demand_ok") if passed else t("check.msg.demand_fail")
    if code == "CHECK_2":
        return t("check.msg.fleet_ok") if passed else t("check.msg.fleet_fail")
    if code == "CHECK_3":
        digits = "".join(char for char in message if char.isdigit())
        number = digits or t("common.na")
        return t("check.msg.minvans", n=number)
    return message


def format_improvement(percentage: float | None) -> str:
    if percentage is None:
        from i18n import t

        return t("common.na")
    value = format_decimal(float(percentage), 1)
    from i18n import current_language

    return f"{value} %" if current_language() == "de" else f"{value}%"


def matrix_km_rows(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    from i18n import t

    node_ids: list[str] = matrix["node_ids"]
    distances: list[list[int]] = matrix["distances_metres"]
    labels = [display_node(node_id) for node_id in node_ids]
    origin_label = t("inspect.col.from")
    rows: list[dict[str, Any]] = []
    for origin, row_metres in zip(node_ids, distances, strict=True):
        row: dict[str, Any] = {origin_label: display_node(origin)}
        for label, metres in zip(labels, row_metres, strict=True):
            row[label] = format_decimal(metres / 1000, 3)
        rows.append(row)
    return rows


def plan_run_status(run: dict[str, Any]) -> str:
    from i18n import t

    status = str(run.get("status") or "")
    if run.get("comparison_eligible") or status == "feasible":
        return t("ux.plan.feasible")
    labels = {
        "heuristic_incomplete": "ux.plan.incomplete",
        "no_solution_found": "ux.plan.no_solution",
    }
    return t(labels.get(status, "ux.plan.incomplete"))


def plans_comparable(baseline: dict[str, Any], optimised: dict[str, Any]) -> bool:
    if not (baseline.get("comparison_eligible") and optimised.get("comparison_eligible")):
        return False
    if baseline.get("scenario_id") != optimised.get("scenario_id"):
        return False
    baseline_total = baseline.get("customers_total")
    optimised_total = optimised.get("customers_total")
    return (
        baseline_total is not None
        and optimised_total is not None
        and baseline_total == optimised_total
    )


def plan_comparison_summary(
    baseline: dict[str, Any], optimised: dict[str, Any]
) -> tuple[str, str | None]:
    from i18n import t

    served_line = t(
        "ux.plan.served.each",
        baseline_served=baseline.get("customers_served"),
        baseline_total=baseline.get("customers_total"),
        optimised_served=optimised.get("customers_served"),
        optimised_total=optimised.get("customers_total"),
        baseline_status=plan_run_status(baseline),
        optimised_status=plan_run_status(optimised),
    )
    if not plans_comparable(baseline, optimised):
        return t("ux.plan.ineligible"), served_line
    return (
        t(
            "ux.plan.result",
            baseline_km=format_km(baseline.get("objective_distance_metres")),
            optimized_km=format_km(optimised.get("objective_distance_metres")),
            reduction=format_improvement(optimised.get("distance_improvement_percentage")),
            customer_count=optimised.get("customers_total"),
        ),
        None,
    )


def operational_summary(baseline: dict[str, Any], optimised: dict[str, Any]) -> str:
    from i18n import t

    baseline_status = status_label(baseline.get("status"))
    optimised_status = status_label(optimised.get("status"))
    if not baseline.get("comparison_eligible"):
        unserved = baseline.get("unserved_customer_ids") or []
        parts = [t("summary.ineligible", status=baseline_status)]
        if unserved:
            parts.append(t("summary.unserved", ids=", ".join(unserved)))
        partial = baseline.get("partial_distance_metres")
        if partial is not None:
            parts.append(t("summary.partial", km=format_km(partial)))
        if optimised.get("comparison_eligible"):
            parts.append(
                t("summary.opt_ok", km=format_km(optimised.get("objective_distance_metres")))
            )
        else:
            parts.append(t("summary.opt_bad", status=optimised_status))
        return " ".join(parts)

    if not optimised.get("comparison_eligible"):
        return t(
            "summary.opt_incomplete",
            km=format_km(baseline.get("objective_distance_metres")),
            status=optimised_status,
        )

    return t(
        "summary.ok",
        base_km=format_km(baseline.get("objective_distance_metres")),
        base_vans=baseline.get("vehicles_used"),
        opt_km=format_km(optimised.get("objective_distance_metres")),
        opt_vans=optimised.get("vehicles_used"),
        improve=format_improvement(optimised.get("distance_improvement_percentage")),
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
    demand = {customer["customer_id"]: customer["demand_totes"] for customer in customers or []}
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
