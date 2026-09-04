"""Page 5: 6-customer example, wired to FastAPI results."""

from __future__ import annotations

import streamlit as st

from api_client import (
    get_routes,
    get_run,
    get_scenario,
    run_baseline,
    run_optimise,
    validate_scenario,
)
from components import (
    boot_page,
    call_api,
    callout,
    page_header,
    render_check_table,
    render_footer,
    section,
    static_table,
    status_badge,
)
from display import (
    format_km,
    format_sequence,
    incomplete_baseline_note,
    matrix_km_rows,
    packing_from_matrix,
    path_distance_metres,
)
from i18n import t
from inspector import attach_leg_distances, incoming_outgoing, selected_arcs
from maps import PLOTLY_CHART_KWARGS, learning_schematic
from state import set_scenario

boot_page()

LEARNING_ID = "LEARNING_6"
BIN_PACKING_ID = "INFEASIBLE_BIN_PACKING"

page_header(t("learn.title"), t("learn.subtitle"), kicker=t("learn.kicker"))

callout(t("learn.callout"))
with st.expander(t("learn.backend"), expanded=True):
    st.markdown(t("learn.backend.body"))

if st.button(t("learn.load"), help=t("learn.load.help")):
    set_scenario(LEARNING_ID)
    st.success(t("learn.loaded"))

scenario = call_api(get_scenario, LEARNING_ID)
if scenario is None:
    st.stop()

matrix = scenario["distance_matrix"]
section(t("learn.inputs"), t("learn.inputs.cap"))
input_metrics = st.columns(3)
input_metrics[0].metric(t("learn.input.demand"), t("unit.totes", n=20))
input_metrics[1].metric(t("learn.input.capacity"), t("unit.fleet", vans=2, cap=10))
input_metrics[2].metric(t("learn.input.rule"), t("learn.input.rule.value"))

section(t("learn.matrix"), t("learn.matrix.cap"))
st.caption(t("learn.matrix.hover"))
from_label = t("inspect.col.from")
matrix_rows = matrix_km_rows(matrix)
matrix_columns = set(matrix_rows[0]) - {from_label}
static_table(matrix_rows, numeric_columns=matrix_columns, row_header=from_label)
st.caption(
    t(
        "learn.matrix.c1",
        km=format_km(path_distance_metres(matrix, ["DEPOT_L6", "C1"])),
    )
)

section(t("learn.demand"), t("learn.demand.cap"))
demand_rows = [
    {
        t("inspect.col.customer"): customer["customer_id"],
        t("dispatch.col.demand"): customer["demand_totes"],
    }
    for customer in scenario["customers"]
]
static_table(
    demand_rows,
    numeric_columns=set(),
    row_header=t("inspect.col.customer"),
)
st.write(t("learn.demand.body"))

section(t("learn.actions"), t("learn.actions.cap"))
col_a, col_b = st.columns(2)
with col_a:
    if st.button(
        t("learn.run.base"),
        type="primary",
        help=t("learn.run.base.help"),
        use_container_width=True,
    ):
        result = call_api(run_baseline, LEARNING_ID)
        if result is not None:
            st.session_state.learning_baseline_run_id = result["run_id"]
            if st.session_state.scenario_id == LEARNING_ID:
                st.session_state.baseline_run_id = result["run_id"]
                st.session_state["_baseline_summary"] = result
with col_b:
    if st.button(
        t("learn.run.opt"),
        help=t("learn.run.opt.help"),
        use_container_width=True,
    ):
        result = call_api(run_optimise, LEARNING_ID, 5)
        if result is not None:
            st.session_state.learning_optimised_run_id = result["run_id"]
            if st.session_state.scenario_id == LEARNING_ID:
                st.session_state.optimised_run_id = result["run_id"]
                st.session_state["_optimised_summary"] = result
st.caption(t("learn.greedy.what"))

baseline = None
optimised = None
if st.session_state.learning_baseline_run_id:
    baseline = call_api(get_run, st.session_state.learning_baseline_run_id)
if st.session_state.learning_optimised_run_id:
    optimised = call_api(get_run, st.session_state.learning_optimised_run_id)

section(t("learn.nn"), t("learn.nn.cap"))
st.markdown(t("learn.nn.steps"))
if baseline is None:
    st.caption(t("learn.nn.need"))
else:
    status_badge(baseline.get("status"), scenario_id=LEARNING_ID)
    note = incomplete_baseline_note(baseline)
    if note:
        st.info(note)
    st.write(t("learn.nn.body"))
    unserved = ", ".join(baseline.get("unserved_customer_ids") or []) or t("common.na")
    baseline_metrics = st.columns(4)
    baseline_metrics[0].metric(
        t("learn.served.label"),
        f"{baseline['customers_served']} / {baseline['customers_total']}",
    )
    baseline_metrics[1].metric(t("learn.unserved.label"), unserved)
    baseline_metrics[2].metric(
        t("learn.partial.label"),
        format_km(baseline.get("partial_distance_metres")),
    )
    baseline_metrics[3].metric(t("learn.complete.label"), t("common.na"))
    routes = call_api(get_routes, baseline["run_id"])
    if routes is not None:
        route_rows = [
            {
                t("table.vehicle"): vehicle["vehicle_id"],
                t("table.sequence"): format_sequence(vehicle.get("sequence") or []),
                t("table.load"): (
                    f"{vehicle['assigned_demand_totes']} / {vehicle['capacity_totes']}"
                ),
                t("table.distance"): format_km(vehicle["route_distance_metres"]),
            }
            for vehicle in routes.get("vehicle_kpis", [])
        ]
        static_table(
            route_rows,
            numeric_columns={t("table.load"), t("table.distance")},
            row_header=t("table.vehicle"),
        )
        sequences = [
            (vehicle["vehicle_id"], vehicle.get("sequence") or [])
            for vehicle in routes.get("vehicle_kpis", [])
            if vehicle.get("is_used")
        ]
        st.plotly_chart(
            learning_schematic(
                sequences,
                unserved_ids=baseline.get("unserved_customer_ids") or [],
            ),
            **PLOTLY_CHART_KWARGS,
        )
        st.caption(t("map.diagram"))
        with st.expander(t("learn.details")):
            arcs = attach_leg_distances(
                selected_arcs(routes.get("vehicle_kpis", [])),
                routes.get("stops", []),
            )
            st.markdown(f"**{t('learn.arcs.nn')}**")
            st.write(t("learn.arcs.help"))
            arc_rows = incoming_outgoing(arcs, matrix["node_ids"])
            static_table(
                arc_rows,
                numeric_columns={
                    "outgoing reconstructed arcs",
                    "incoming reconstructed arcs",
                },
                row_header="node",
            )

section(t("learn.pack"), t("learn.pack.cap"))
packing = packing_from_matrix(matrix, scenario["customers"])
st.info(t("packing.note"))
st.write(t("learn.pack.body"))
packing_rows = [
    {
        t("table.vehicle"): route["vehicle_id"],
        t("table.pack"): ", ".join(route["pack"]),
        t("table.sequence"): format_sequence(route["sequence"]),
        t("table.load"): route["load_totes"],
        t("table.distance"): format_km(route["distance_metres"]),
    }
    for route in packing["routes"]
]
static_table(
    packing_rows,
    numeric_columns={t("table.load"), t("table.distance")},
    row_header=t("table.vehicle"),
)
st.metric(t("learn.pack.total"), format_km(packing["total_distance_metres"]))
st.plotly_chart(
    learning_schematic(
        [(route["vehicle_id"], route["sequence"]) for route in packing["routes"]]
    ),
    **PLOTLY_CHART_KWARGS,
)
st.caption(t("map.diagram"))

section(t("learn.opt"), t("learn.opt.cap"))
if optimised is None:
    st.caption(t("learn.opt.need"))
else:
    status_badge(optimised.get("status"), scenario_id=LEARNING_ID)
    st.write(t("learn.opt.obj", km=format_km(optimised.get("objective_distance_metres"))))
    st.write(t("learn.opt.body"))
    routes = call_api(get_routes, optimised["run_id"])
    if routes is not None:
        route_rows = [
            {
                t("table.vehicle"): vehicle["vehicle_id"],
                t("table.sequence"): format_sequence(vehicle.get("sequence") or []),
                t("table.load"): (
                    f"{vehicle['assigned_demand_totes']} / {vehicle['capacity_totes']}"
                ),
                t("table.distance"): format_km(vehicle["route_distance_metres"]),
            }
            for vehicle in routes.get("vehicle_kpis", [])
        ]
        static_table(
            route_rows,
            numeric_columns={t("table.load"), t("table.distance")},
            row_header=t("table.vehicle"),
        )
        sequences = [
            (vehicle["vehicle_id"], vehicle.get("sequence") or [])
            for vehicle in routes.get("vehicle_kpis", [])
            if vehicle.get("is_used")
        ]
        st.plotly_chart(
            learning_schematic(sequences),
            **PLOTLY_CHART_KWARGS,
        )
        st.caption(t("map.diagram"))
        with st.expander(t("learn.details")):
            arcs = attach_leg_distances(
                selected_arcs(routes.get("vehicle_kpis", [])),
                routes.get("stops", []),
            )
            st.markdown(f"**{t('learn.arcs.opt')}**")
            arc_rows = incoming_outgoing(arcs, matrix["node_ids"])
            static_table(
                arc_rows,
                numeric_columns={
                    "outgoing reconstructed arcs",
                    "incoming reconstructed arcs",
                },
                row_header="node",
            )

section(t("learn.why"))
st.write(t("learn.why.body"))

with st.expander(t("learn.edge")):
    st.caption(t("learn.edge.cap"))
    section(t("learn.bin"), t("learn.bin.cap"))
    st.write(t("learn.bin.body"))
    bin_a, bin_b = st.columns(2)
    with bin_a:
        if st.button(t("learn.bin.validate"), help=t("learn.bin.validate.help")):
            result = call_api(validate_scenario, BIN_PACKING_ID)
            if result is not None:
                st.session_state["_bin_validate"] = result
    with bin_b:
        if st.button(t("learn.bin.optimise"), help=t("learn.bin.optimise.help")):
            result = call_api(run_optimise, BIN_PACKING_ID, 5)
            if result is not None:
                st.session_state["_bin_optimise"] = result

    if st.session_state.get("_bin_validate"):
        status_badge(
            st.session_state["_bin_validate"].get("status"),
            scenario_id=BIN_PACKING_ID,
        )
        render_check_table(st.session_state["_bin_validate"].get("checks", []))
    if st.session_state.get("_bin_optimise"):
        status_badge(
            st.session_state["_bin_optimise"].get("status"),
            scenario_id=BIN_PACKING_ID,
        )
        st.write(st.session_state["_bin_optimise"].get("message") or "")
        st.caption(t("learn.bin.caption"))

render_footer()
