"""Page 2: inspect reconstructed routes for the selected run."""

from __future__ import annotations

import streamlit as st

from api_client import get_routes, get_run, get_scenario
from components import (
    boot_page,
    call_api,
    empty_state,
    export_buttons,
    page_header,
    render_footer,
    section,
    static_table,
    status_badge,
    vehicle_card,
)
from display import format_km, format_sequence, incomplete_baseline_note
from i18n import t
from maps import PLOTLY_CHART_KWARGS, learning_schematic, route_map
from state import summary_for_current

boot_page()

page_header(t("routes.title"), t("routes.subtitle"), kicker=t("routes.kicker"))

options = []
optimised = summary_for_current("optimised")
baseline = summary_for_current("baseline")
if optimised:
    options.append((t("routes.opt"), optimised["run_id"]))
if baseline:
    options.append((t("routes.base"), baseline["run_id"]))

if not options:
    empty_state(t("routes.empty.title"), t("routes.empty.body"))
    render_footer()
    st.stop()

labels = [item[0] for item in options]
choice = st.radio(
    t("routes.pick"),
    labels,
    horizontal=True,
    help=t("routes.pick.help"),
)
run_id = dict(options)[choice]

run_payload = call_api(get_run, run_id)
routes_payload = call_api(get_routes, run_id)
scenario_payload = call_api(get_scenario, st.session_state.scenario_id)
if run_payload is None or routes_payload is None or scenario_payload is None:
    st.stop()

status_badge(run_payload.get("status"))
note = incomplete_baseline_note(run_payload)
if note:
    st.info(note)
if run_payload.get("scenario_id") != st.session_state.scenario_id:
    st.error(t("routes.mismatch"))
    st.stop()

section(t("routes.kpis"), t("routes.kpis.cap"))
cols = st.columns(4)
cols[0].metric(
    t("routes.m.served"),
    f"{run_payload['customers_served']} / {run_payload['customers_total']}",
    help=t("routes.m.served.help"),
)
cols[1].metric(
    t("routes.m.demand"),
    t("unit.totes", n=run_payload["demand_served_totes"]),
    help=t("tote.help"),
)
cols[2].metric(
    t("routes.m.vans"),
    f"{run_payload['vehicles_used']} / {run_payload['vehicles_available']}",
    help=t("routes.m.vans.help"),
)
if run_payload.get("comparison_eligible"):
    cols[3].metric(
        t("routes.m.total"),
        format_km(run_payload.get("objective_distance_metres")),
        help=t("routes.m.total.help"),
    )
else:
    cols[3].metric(
        t("routes.m.partial"),
        format_km(run_payload.get("partial_distance_metres")),
        help=t("routes.m.partial.help"),
    )

export_buttons(run_id)

if run_payload.get("unserved_customer_ids"):
    st.warning(t("routes.unserved", ids=", ".join(run_payload["unserved_customer_ids"])))

geographic = scenario_payload["scenario"].get("has_geographic_coordinates")
if geographic:
    section(t("routes.map"), t("routes.map.cap"))
    st.plotly_chart(
        route_map(
            scenario_payload,
            routes_payload,
            unserved_ids=run_payload.get("unserved_customer_ids") or [],
        ),
        **PLOTLY_CHART_KWARGS,
    )
    st.caption(t("map.schematic"))
elif st.session_state.scenario_id == "LEARNING_6":
    section(t("routes.diagram"), t("routes.diagram.cap"))
    st.info(t("routes.nogeo.l6"))
    sequences = [
        (vehicle["vehicle_id"], vehicle.get("sequence") or [])
        for vehicle in routes_payload.get("vehicle_kpis", [])
        if vehicle.get("is_used")
    ]
    st.plotly_chart(
        learning_schematic(
            sequences,
            unserved_ids=run_payload.get("unserved_customer_ids") or [],
        ),
        **PLOTLY_CHART_KWARGS,
    )
    st.caption(t("map.diagram"))
else:
    st.info(t("routes.nogeo"))

section(t("routes.seq"))
stop_rows = [
    {
        t("table.vehicle"): vehicle["vehicle_id"],
        t("table.used"): t("common.yes") if vehicle["is_used"] else t("common.no"),
        t("table.sequence"): format_sequence(vehicle.get("sequence") or []),
        t("table.orders"): str(vehicle["customer_count"]),
        t("table.load"): f"{vehicle['assigned_demand_totes']} / {vehicle['capacity_totes']}",
        t("table.distance"): format_km(vehicle["route_distance_metres"]),
    }
    for vehicle in routes_payload.get("vehicle_kpis", [])
]
static_table(
    stop_rows,
    numeric_columns={
        t("table.orders"),
        t("table.load"),
        t("table.distance"),
    },
    row_header=t("table.vehicle"),
)

section(t("routes.cards"), t("routes.cards.cap"))
used = [
    vehicle for vehicle in routes_payload.get("vehicle_kpis", []) if vehicle.get("is_used")
]
unused = [
    vehicle
    for vehicle in routes_payload.get("vehicle_kpis", [])
    if not vehicle.get("is_used")
]
for vehicle in used:
    vehicle_card(vehicle)
if unused:
    st.markdown(f"**{t('routes.unused')}**")
    unused_cols = st.columns(min(len(unused), 4))
    for column, vehicle in zip(unused_cols, unused, strict=False):
        with column:
            vehicle_card(vehicle)

render_footer()
