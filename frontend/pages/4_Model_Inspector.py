"""Page 4: reconstruct MILP symbols from returned routes."""

from __future__ import annotations

import streamlit as st

from api_client import get_checks, get_routes, get_run, get_scenario
from components import (
    call_api,
    callout,
    empty_state,
    page_header,
    render_footer,
    section,
    status_badge,
)
from display import display_node, format_km, matrix_km_rows
from i18n import t
from inspector import (
    attach_leg_distances,
    cumulative_loads,
    incoming_outgoing,
    route_matrix,
    selected_arcs,
)
from state import summary_for_current

page_header(t("nav.inspect"), t("inspect.subtitle"))

options = []
optimised = summary_for_current("optimised")
baseline = summary_for_current("baseline")
if optimised:
    options.append((t("routes.opt"), optimised["run_id"]))
if baseline:
    options.append((t("routes.base"), baseline["run_id"]))
if not options:
    empty_state(t("inspect.empty.title"), t("inspect.empty.body"))
    render_footer()
    st.stop()

choice = st.radio(
    t("inspect.pick"),
    [item[0] for item in options],
    horizontal=True,
    help=t("inspect.pick.help"),
)
run_id = dict(options)[choice]

run_payload = call_api(get_run, run_id)
routes_payload = call_api(get_routes, run_id)
checks_payload = call_api(get_checks, run_id)
scenario_payload = call_api(get_scenario, st.session_state.scenario_id)
if None in (run_payload, routes_payload, checks_payload, scenario_payload):
    st.stop()

status_badge(run_payload.get("status"), run_type=run_payload.get("run_type"))
callout(t("inspect.how"))

if run_payload.get("run_type") == "optimised":
    section(t("inspect.solver"), t("inspect.solver.cap"))
    st.write(t("inspect.solver.strategy"))
    st.write(t("inspect.solver.time", n=run_payload.get("solver_time_limit_seconds")))
    st.write(t("inspect.solver.term", term=run_payload.get("solver_termination")))
    st.write(t("inspect.solver.runtime", n=run_payload.get("solver_runtime_seconds")))
else:
    st.caption(t("ux.inspect.baseline"))

section(t("inspect.demand"), t("inspect.demand.cap"))
st.dataframe(
    [
        {
            t("inspect.col.customer"): item["customer_id"],
            t("inspect.col.required"): item["demand_totes"],
            t("inspect.col.delivered"): item["demand_totes"] if item["service_count"] == 1 else 0,
            t("inspect.col.vehicle"): item.get("assigned_vehicle") or t("common.na"),
            t("inspect.col.visits"): item["service_count"],
            t("inspect.col.check"): item["demand_check"],
        }
        for item in checks_payload.get("assignments", [])
    ],
    use_container_width=True,
    hide_index=True,
)

section(t("inspect.constraints"), t("inspect.constraints.cap"))
st.dataframe(checks_payload.get("checks", []), use_container_width=True, hide_index=True)

section(t("inspect.loads"), t("inspect.loads.cap"))
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
section(t("inspect.arcs"), t("inspect.arcs.cap"))
st.dataframe(incoming_outgoing(arcs, node_ids), use_container_width=True, hide_index=True)

section(t("inspect.arcs.list"))
compact_rows = [
    {
        t("table.vehicle"): arc["vehicle_id"],
        t("inspect.col.from"): arc["from"],
        t("inspect.col.to"): arc["to"],
        t("inspect.col.selected"): arc["reconstructed_x"],
        t("inspect.col.leg"): arc["distance"],
    }
    for arc in arcs
]
is_learning = st.session_state.scenario_id == "LEARNING_6"
if is_learning:
    st.dataframe(compact_rows, use_container_width=True, hide_index=True)
    for vehicle in routes_payload.get("vehicle_kpis", []):
        if not vehicle.get("is_used"):
            continue
        st.markdown(t("inspect.matrix.van", id=vehicle["vehicle_id"]))
        st.dataframe(
            route_matrix(node_ids, vehicle.get("sequence") or []),
            use_container_width=True,
            hide_index=True,
        )
else:
    st.dataframe(compact_rows, use_container_width=True, hide_index=True)
    with st.expander(t("inspect.matrix.all")):
        for vehicle in routes_payload.get("vehicle_kpis", []):
            if not vehicle.get("is_used"):
                continue
            st.markdown(f"{vehicle['vehicle_id']}")
            st.dataframe(
                route_matrix(node_ids, vehicle.get("sequence") or []),
                use_container_width=True,
                hide_index=True,
            )

section(t("inspect.dist"), t("inspect.dist.cap"))
if is_learning:
    st.dataframe(
        matrix_km_rows(scenario_payload["distance_matrix"]),
        use_container_width=True,
        hide_index=True,
    )
else:
    with st.expander(t("inspect.dist.full"), expanded=False):
        st.dataframe(
            matrix_km_rows(scenario_payload["distance_matrix"]),
            use_container_width=True,
            hide_index=True,
        )

depot_id = scenario_payload["depot"]["depot_id"]
st.caption(t("inspect.depot", id=depot_id, label=display_node(depot_id)))
st.caption(t("inspect.obj", km=format_km(run_payload.get("objective_distance_metres"))))

st.page_link("pages/3_Baseline_vs_Optimised.py", label=t("nav.compare"))
render_footer()
