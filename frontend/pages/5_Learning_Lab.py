"""Page 5: LEARNING_6 teaching lab, wired to FastAPI results."""

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
from components import call_api, inject_theme, render_sidebar, status_badge
from display import (
    format_km,
    format_sequence,
    incomplete_baseline_note,
    matrix_km_rows,
    packing_from_matrix,
    path_distance_metres,
)
from inspector import attach_leg_distances, incoming_outgoing, selected_arcs
from maps import DIAGRAM_CAPTION, PLOTLY_CHART_KWARGS, learning_schematic
from state import ensure_session, set_scenario

ensure_session()
inject_theme()
render_sidebar()

LEARNING_ID = "LEARNING_6"
BIN_PACKING_ID = "INFEASIBLE_BIN_PACKING"

st.title("Learning Lab")
st.caption(
    "Six-customer teaching fixture. Every distance and status on this page comes from "
    "the FastAPI backend matrix and planning endpoints."
)

if st.button("Load LEARNING_6 into the planner"):
    set_scenario(LEARNING_ID)
    st.success("Planner scenario set to LEARNING_6.")

scenario = call_api(get_scenario, LEARNING_ID)
if scenario is None:
    st.stop()

matrix = scenario["distance_matrix"]
st.markdown("**How to read the distance matrix**")
st.write(
    f"Stored depot id `{scenario['depot']['depot_id']}` is shown as Depot. "
    "Cell (Depot, C1) should be 3.000 km."
)
st.dataframe(matrix_km_rows(matrix), use_container_width=True, hide_index=True)
st.caption(
    f"Backend matrix Depot → C1 = {format_km(path_distance_metres(matrix, ['DEPOT_L6', 'C1']))}."
)

demand_rows = [
    {"Customer": customer["customer_id"], "Demand (totes)": customer["demand_totes"]}
    for customer in scenario["customers"]
]
st.markdown("**Demand and capacity**")
st.dataframe(demand_rows, hide_index=True, use_container_width=True)
st.write(
    "Total demand 20 totes, two vans of 10 totes. Unsplit deliveries mean each pack must "
    "sum to exactly 10. Sequential nearest neighbour can still fail on this tight instance."
)

col_a, col_b = st.columns(2)
with col_a:
    if st.button("Run LEARNING_6 baseline", type="primary"):
        result = call_api(run_baseline, LEARNING_ID)
        if result is not None:
            st.session_state.learning_baseline_run_id = result["run_id"]
            if st.session_state.scenario_id == LEARNING_ID:
                st.session_state.baseline_run_id = result["run_id"]
with col_b:
    if st.button("Run LEARNING_6 optimiser"):
        result = call_api(run_optimise, LEARNING_ID, 5)
        if result is not None:
            st.session_state.learning_optimised_run_id = result["run_id"]
            if st.session_state.scenario_id == LEARNING_ID:
                st.session_state.optimised_run_id = result["run_id"]

baseline = None
optimised = None
if st.session_state.learning_baseline_run_id:
    baseline = call_api(get_run, st.session_state.learning_baseline_run_id)
if st.session_state.learning_optimised_run_id:
    optimised = call_api(get_run, st.session_state.learning_optimised_run_id)

st.markdown("**Sequential nearest neighbour**")
if baseline is None:
    st.caption("Run the LEARNING_6 baseline to load the actual API result.")
else:
    status_badge(baseline.get("status"))
    note = incomplete_baseline_note(baseline)
    if note:
        st.info(note)
    st.write(
        "The heuristic is `heuristic_incomplete` on this fixture: C4 is left unserved, "
        "so the plan is not comparison-eligible and must not be labelled 34.000 km."
    )
    st.write(f"Customers served: {baseline['customers_served']} / {baseline['customers_total']}")
    st.write(f"Unserved: {', '.join(baseline.get('unserved_customer_ids') or []) or '—'}")
    st.write(f"Partial constructed distance: {format_km(baseline.get('partial_distance_metres'))}")
    st.write("Objective distance: —")
    routes = call_api(get_routes, baseline["run_id"])
    if routes is not None:
        st.dataframe(
            [
                {
                    "vehicle_id": vehicle["vehicle_id"],
                    "sequence": format_sequence(vehicle.get("sequence") or []),
                    "load": f"{vehicle['assigned_demand_totes']} / {vehicle['capacity_totes']}",
                    "distance": format_km(vehicle["route_distance_metres"]),
                }
                for vehicle in routes.get("vehicle_kpis", [])
            ],
            hide_index=True,
            use_container_width=True,
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
        st.caption(DIAGRAM_CAPTION)
        arcs = attach_leg_distances(
            selected_arcs(routes.get("vehicle_kpis", [])),
            routes.get("stops", []),
        )
        st.markdown("**Reconstructed x_ijk from consecutive NN stops**")
        st.write(
            "An outgoing row sum is how many selected reconstructed arcs leave the node. "
            "An incoming column sum is how many arrive. These are not native OR-Tools variables."
        )
        st.dataframe(
            incoming_outgoing(arcs, matrix["node_ids"]),
            hide_index=True,
            use_container_width=True,
        )

st.markdown("**34.000 km named reference packing**")
packing = packing_from_matrix(matrix, scenario["customers"])
st.info(packing["note"])
st.write(
    "Leg lengths are looked up in the backend LEARNING_6 matrix. "
    "This packing is not sequential nearest neighbour."
)
st.dataframe(
    [
        {
            "vehicle_id": route["vehicle_id"],
            "pack": ", ".join(route["pack"]),
            "sequence": format_sequence(route["sequence"]),
            "load_totes": route["load_totes"],
            "distance": format_km(route["distance_metres"]),
        }
        for route in packing["routes"]
    ],
    hide_index=True,
    use_container_width=True,
)
st.metric("Reference packing total", format_km(packing["total_distance_metres"]))
st.plotly_chart(
    learning_schematic(
        [(route["vehicle_id"], route["sequence"]) for route in packing["routes"]]
    ),
    **PLOTLY_CHART_KWARGS,
)
st.caption(DIAGRAM_CAPTION)

st.markdown("**OR-Tools verified optimum**")
if optimised is None:
    st.caption("Run the LEARNING_6 optimiser to load the actual API result.")
else:
    status_badge(optimised.get("status"))
    st.write(f"Objective: {format_km(optimised.get('objective_distance_metres'))}")
    st.write(
        "The 31.000 km assignment packs {C1, C5, C6} and {C2, C3, C4}. "
        "That packing is shorter than the 34.000 km reference because a feasible "
        "pack is not automatically the shortest tour of those customers."
    )
    routes = call_api(get_routes, optimised["run_id"])
    if routes is not None:
        st.dataframe(
            [
                {
                    "vehicle_id": vehicle["vehicle_id"],
                    "sequence": format_sequence(vehicle.get("sequence") or []),
                    "load": f"{vehicle['assigned_demand_totes']} / {vehicle['capacity_totes']}",
                    "distance": format_km(vehicle["route_distance_metres"]),
                }
                for vehicle in routes.get("vehicle_kpis", [])
            ],
            hide_index=True,
            use_container_width=True,
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
        st.caption(DIAGRAM_CAPTION)
        arcs = attach_leg_distances(
            selected_arcs(routes.get("vehicle_kpis", [])),
            routes.get("stops", []),
        )
        st.markdown("**Reconstructed x_ijk from consecutive optimiser stops**")
        st.dataframe(
            incoming_outgoing(arcs, matrix["node_ids"]),
            hide_index=True,
            use_container_width=True,
        )

st.markdown("**Why nearest feasible is not globally shortest**")
st.write(
    "From C2, sequential nearest neighbour takes feasible C3 at 3.000 km and then cannot "
    "fit C4. A globally better packing leaves C3 for the other van. Local greedy choice "
    "blocks the only remaining 5-tote order."
)

st.markdown("**Bin-packing teaching fixture**")
st.write(
    "`INFEASIBLE_BIN_PACKING` has three 6-tote orders and two 10-tote vans. "
    "Checks 1 and 2 pass (6 ≤ 10 and 18 ≤ 20), but no unsplit assignment exists."
)
if st.button("Validate INFEASIBLE_BIN_PACKING"):
    result = call_api(validate_scenario, BIN_PACKING_ID)
    if result is not None:
        st.session_state["_bin_validate"] = result
if st.button("Optimise INFEASIBLE_BIN_PACKING"):
    result = call_api(run_optimise, BIN_PACKING_ID, 5)
    if result is not None:
        st.session_state["_bin_optimise"] = result

if st.session_state.get("_bin_validate"):
    status_badge(st.session_state["_bin_validate"].get("status"))
    st.dataframe(
        st.session_state["_bin_validate"].get("checks", []),
        hide_index=True,
        use_container_width=True,
    )
if st.session_state.get("_bin_optimise"):
    status_badge(st.session_state["_bin_optimise"].get("status"))
    st.write(st.session_state["_bin_optimise"].get("message") or "")
    st.caption("A missing complete plan is `no_solution_found`, not `infeasible`.")
