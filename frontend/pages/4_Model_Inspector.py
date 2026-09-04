"""Page 4: reconstruct MILP symbols from returned routes."""

from __future__ import annotations

import streamlit as st

from api_client import get_checks, get_routes, get_run, get_scenario
from components import call_api, inject_theme, render_sidebar, status_badge
from display import display_node, format_km, matrix_km_rows
from inspector import (
    attach_leg_distances,
    cumulative_loads,
    incoming_outgoing,
    route_matrix,
    selected_arcs,
)
from state import ensure_session, summary_for_current

ensure_session()
inject_theme()
render_sidebar()

st.title("Model Inspector")
st.caption(
    "Displayed x, y, and loads are reconstructed from stop sequences. "
    "OR-Tools RoutingModel does not solve the documented three-index MILP directly. "
    "Loads are cumulative tote counts, not MTZ potentials w_ik."
)

options = []
optimised = summary_for_current("optimised")
baseline = summary_for_current("baseline")
if optimised:
    options.append(("Optimised", optimised["run_id"]))
if baseline:
    options.append(("Baseline", baseline["run_id"]))
if not options:
    st.warning("Run a plan on Dispatch Setup first.")
    st.stop()

choice = st.radio("Plan to inspect", [item[0] for item in options], horizontal=True)
run_id = dict(options)[choice]

run_payload = call_api(get_run, run_id)
routes_payload = call_api(get_routes, run_id)
checks_payload = call_api(get_checks, run_id)
scenario_payload = call_api(get_scenario, st.session_state.scenario_id)
if None in (run_payload, routes_payload, checks_payload, scenario_payload):
    st.stop()

status_badge(run_payload.get("status"))
st.markdown("**Solver configuration**")
st.write(
    "First-solution strategy: `PATH_CHEAPEST_ARC`. Local search: `GUIDED_LOCAL_SEARCH`. "
    "These are the configured OR-Tools settings, not native MILP variables."
)
st.write(f"Time limit requested: {st.session_state.solver_time_limit_seconds} s")
st.write(f"Solver termination: `{run_payload.get('solver_termination')}`")
st.write(f"Solver runtime: {run_payload.get('solver_runtime_seconds') or '—'} s")

st.markdown("**Demand-satisfaction table**")
st.caption("One row per customer. Service count must be 1 on a complete feasible plan.")
st.dataframe(
    [
        {
            "Customer": item["customer_id"],
            "Required": item["demand_totes"],
            "Delivered": item["demand_totes"] if item["service_count"] == 1 else 0,
            "Vehicle": item.get("assigned_vehicle") or "—",
            "Visit Count": item["service_count"],
            "Check": item["demand_check"],
        }
        for item in checks_payload.get("assignments", [])
    ],
    use_container_width=True,
    hide_index=True,
)

st.markdown("**Constraint reconciliation**")
st.dataframe(checks_payload.get("checks", []), use_container_width=True, hide_index=True)

st.markdown("**Reconstructed cumulative loads**")
st.caption("These values are running tote totals along the returned sequence. They are not w_ik.")
st.dataframe(
    cumulative_loads(routes_payload.get("stops", [])),
    use_container_width=True,
    hide_index=True,
)

arcs = attach_leg_distances(
    selected_arcs(routes_payload.get("vehicle_kpis", [])),
    routes_payload.get("stops", []),
)
node_ids = scenario_payload["distance_matrix"]["node_ids"]
st.markdown("**Incoming and outgoing selected arcs**")
st.caption(
    "Outgoing row sums are reconstructed departures. "
    "Incoming column sums are reconstructed arrivals. "
    "Both are built from consecutive stops, not from OR-Tools native x_ijk."
)
st.dataframe(incoming_outgoing(arcs, node_ids), use_container_width=True, hide_index=True)

st.markdown("**Selected reconstructed arcs**")
compact_rows = [
    {
        "vehicle_id": arc["vehicle_id"],
        "from": arc["from"],
        "to": arc["to"],
        "reconstructed x": arc["reconstructed_x"],
        "leg distance": arc["distance"],
    }
    for arc in arcs
]
is_learning = st.session_state.scenario_id == "LEARNING_6"
if is_learning:
    st.dataframe(compact_rows, use_container_width=True, hide_index=True)
    for vehicle in routes_payload.get("vehicle_kpis", []):
        if not vehicle.get("is_used"):
            continue
        st.markdown(f"Reconstructed route matrix for {vehicle['vehicle_id']}")
        st.dataframe(
            route_matrix(node_ids, vehicle.get("sequence") or []),
            use_container_width=True,
            hide_index=True,
        )
else:
    st.dataframe(compact_rows, use_container_width=True, hide_index=True)
    with st.expander("Full reconstructed route matrices"):
        for vehicle in routes_payload.get("vehicle_kpis", []):
            if not vehicle.get("is_used"):
                continue
            st.markdown(f"{vehicle['vehicle_id']}")
            st.dataframe(
                route_matrix(node_ids, vehicle.get("sequence") or []),
                use_container_width=True,
                hide_index=True,
            )

st.markdown("**Distance matrix**")
st.caption("Values are backend metres displayed as kilometres to three decimal places.")
if is_learning:
    st.dataframe(
        matrix_km_rows(scenario_payload["distance_matrix"]),
        use_container_width=True,
        hide_index=True,
    )
else:
    with st.expander("Full distance matrix", expanded=False):
        st.dataframe(
            matrix_km_rows(scenario_payload["distance_matrix"]),
            use_container_width=True,
            hide_index=True,
        )
    st.markdown("Compact selected-arc distances")
    st.dataframe(compact_rows, use_container_width=True, hide_index=True)

depot_id = scenario_payload["depot"]["depot_id"]
st.caption(f"Stored depot identifier `{depot_id}` is displayed as `{display_node(depot_id)}`.")
st.caption(
    f"Objective distance from the run: "
    f"{format_km(run_payload.get('objective_distance_metres'))}"
)
