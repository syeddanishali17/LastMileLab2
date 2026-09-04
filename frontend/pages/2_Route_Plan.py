"""Page 2: inspect reconstructed routes for the selected run."""

from __future__ import annotations

import streamlit as st

from api_client import get_routes, get_run, get_scenario
from components import (
    call_api,
    export_buttons,
    inject_theme,
    render_sidebar,
    status_badge,
    vehicle_card,
)
from display import MAP_CAPTION, format_km, format_sequence, incomplete_baseline_note
from maps import DIAGRAM_CAPTION, PLOTLY_CHART_KWARGS, learning_schematic, route_map
from state import ensure_session, summary_for_current

ensure_session()
inject_theme()
render_sidebar()

st.title("Route Plan")
st.caption("Reconstructed stop sequences from the selected FastAPI run.")

options = []
optimised = summary_for_current("optimised")
baseline = summary_for_current("baseline")
if optimised:
    options.append(("Optimised", optimised["run_id"]))
if baseline:
    options.append(("Baseline", baseline["run_id"]))

if not options:
    st.warning("Run a baseline or optimisation on Dispatch Setup first.")
    st.stop()

labels = [item[0] for item in options]
choice = st.radio("Plan to display", labels, horizontal=True)
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
    st.error(
        "This run belongs to a different scenario. "
        "Load and solve the active scenario again."
    )
    st.stop()
cols = st.columns(4)
cols[0].metric(
    "Customers served",
    f"{run_payload['customers_served']} / {run_payload['customers_total']}",
)
cols[1].metric("Demand served", f"{run_payload['demand_served_totes']} totes")
cols[2].metric("Vans used", f"{run_payload['vehicles_used']} / {run_payload['vehicles_available']}")
if run_payload.get("comparison_eligible"):
    cols[3].metric("Total distance", format_km(run_payload.get("objective_distance_metres")))
else:
    cols[3].metric("Partial distance", format_km(run_payload.get("partial_distance_metres")))

export_buttons(run_id)

if run_payload.get("unserved_customer_ids"):
    st.warning("Unserved: " + ", ".join(run_payload["unserved_customer_ids"]))

geographic = scenario_payload["scenario"].get("has_geographic_coordinates")
if geographic:
    st.plotly_chart(
        route_map(
            scenario_payload,
            routes_payload,
            unserved_ids=run_payload.get("unserved_customer_ids") or [],
        ),
        **PLOTLY_CHART_KWARGS,
    )
    st.caption(MAP_CAPTION)
elif st.session_state.scenario_id == "LEARNING_6":
    st.info("No geographic coordinates. Routes are shown as a schematic diagram and tables.")
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
    st.caption(DIAGRAM_CAPTION)
else:
    st.info("No geographic coordinates. Routes are shown as tables only.")

st.markdown("**Route sequences**")
st.dataframe(
    [
        {
            "vehicle_id": vehicle["vehicle_id"],
            "used": vehicle["is_used"],
            "sequence": format_sequence(vehicle.get("sequence") or []),
            "orders": vehicle["customer_count"],
            "load_totes": f"{vehicle['assigned_demand_totes']} / {vehicle['capacity_totes']}",
            "distance": format_km(vehicle["route_distance_metres"]),
        }
        for vehicle in routes_payload.get("vehicle_kpis", [])
    ],
    use_container_width=True,
    hide_index=True,
)

st.markdown("**Vehicle cards**")
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
    st.markdown("**Unused vans**")
    unused_cols = st.columns(min(len(unused), 4))
    for column, vehicle in zip(unused_cols, unused, strict=False):
        with column:
            vehicle_card(vehicle)
