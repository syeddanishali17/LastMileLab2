"""Page 1: load, validate, and solve a dispatch scenario."""

from __future__ import annotations

import streamlit as st

from api_client import (
    generate_scenario,
    get_scenario,
    list_scenarios,
    run_baseline,
    run_optimise,
    validate_scenario,
)
from components import call_api, inject_theme, render_sidebar, status_badge
from display import format_km, format_pct, incomplete_baseline_note, matrix_km_rows
from maps import PLOTLY_CHART_KWARGS, customer_map
from state import ensure_session, set_scenario, summary_for_current

ensure_session()
inject_theme()
render_sidebar()

st.title("Dispatch Setup")
st.caption("Understand demand, capacity, and feasibility before solving.")

FIXED = ["LEARNING_6", "VIENNA_STANDARD_24"]
TEACHING = [
    "INFEASIBLE_SINGLE_OVERSIZE",
    "INFEASIBLE_FLEET_OVERFLOW",
    "INFEASIBLE_BIN_PACKING",
]

listed = call_api(list_scenarios) or []
known_ids = [item["scenario_id"] for item in listed]
generated_ids = [
    scenario_id
    for scenario_id in known_ids
    if scenario_id.startswith("GEN_")
]
choices = [*FIXED, *generated_ids, *TEACHING]
current = st.session_state.scenario_id
if current not in choices:
    choices = [current, *choices]

selected = st.selectbox(
    "Scenario",
    options=choices,
    index=choices.index(current) if current in choices else 0,
)
if selected != st.session_state.scenario_id:
    st.warning(
        f"`{selected}` is selected but not loaded. Click Load Scenario before solving."
    )

if st.session_state.solver_time_limit_seconds not in (1, 5, 10):
    st.session_state.solver_time_limit_seconds = 5
st.selectbox(
    "OR-Tools time limit (seconds)",
    options=[1, 5, 10],
    key="solver_time_limit_seconds",
    help="The API accepts 1, 5, or 10 seconds.",
)

col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    load_clicked = st.button("Load Scenario", type="primary")
with col_b:
    validate_clicked = st.button("Validate Scenario")
with col_c:
    baseline_clicked = st.button("Run Baseline")
with col_d:
    optimise_clicked = st.button("Run Optimisation")

if load_clicked:
    payload = call_api(get_scenario, selected)
    if payload is not None:
        set_scenario(selected)
        st.session_state["_scenario_payload"] = payload
        st.success(f"Loaded `{selected}`.")

payload = st.session_state.get("_scenario_payload")
loaded_id = None if payload is None else payload.get("scenario", {}).get("scenario_id")
if payload is None or loaded_id != st.session_state.scenario_id:
    payload = call_api(get_scenario, st.session_state.scenario_id)
    if payload is not None:
        st.session_state["_scenario_payload"] = payload

if validate_clicked:
    result = call_api(validate_scenario, st.session_state.scenario_id)
    if result is not None:
        st.session_state["_validate_result"] = result

if baseline_clicked:
    result = call_api(run_baseline, st.session_state.scenario_id)
    if result is not None:
        st.session_state.baseline_run_id = result["run_id"]
        st.session_state["_baseline_summary"] = result

if optimise_clicked:
    result = call_api(
        run_optimise,
        st.session_state.scenario_id,
        st.session_state.solver_time_limit_seconds,
    )
    if result is not None:
        st.session_state.optimised_run_id = result["run_id"]
        st.session_state["_optimised_summary"] = result

with st.expander("Generate a synthetic geographic scenario"):
    st.caption("The generator stores the scenario in the running API process only.")
    seed = st.number_input("random_seed", min_value=0, max_value=2147483647, value=42, step=1)
    n_customers = st.number_input("customer_count", min_value=1, max_value=50, value=24, step=1)
    n_vehicles = st.number_input("vehicle_count", min_value=1, max_value=10, value=4, step=1)
    capacity = st.number_input(
        "vehicle_capacity_totes",
        min_value=1,
        max_value=100,
        value=30,
        step=1,
    )
    detour = st.number_input("detour_factor", min_value=1.00, max_value=2.00, value=1.25, step=0.01)
    z1 = st.number_input("Z1 weight", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    z2 = st.number_input("Z2 weight", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    z3 = st.number_input("Z3 weight", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    z4 = st.number_input("Z4 weight", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
    if st.button("Generate scenario"):
        generated = call_api(
            generate_scenario,
            {
                "random_seed": int(seed),
                "customer_count": int(n_customers),
                "vehicle_count": int(n_vehicles),
                "vehicle_capacity_totes": int(capacity),
                "detour_factor": round(float(detour), 2),
                "geographic_zone_weights": {"Z1": z1, "Z2": z2, "Z3": z3, "Z4": z4},
            },
        )
        if generated is not None:
            set_scenario(generated["scenario_id"])
            loaded = call_api(get_scenario, generated["scenario_id"])
            if loaded is not None:
                st.session_state["_scenario_payload"] = loaded
            st.success(f"Generated `{generated['scenario_id']}`.")
            st.rerun()

if payload is None:
    st.stop()

scenario = payload["scenario"]
customers = payload["customers"]
vehicles = payload["vehicles"]
precheck = payload["precheck"]
total_demand = sum(customer["demand_totes"] for customer in customers)
fleet_capacity = scenario["vehicle_count"] * scenario["vehicle_capacity_totes"]
ratio = total_demand / fleet_capacity if fleet_capacity else None

metrics = st.columns(4)
metrics[0].metric("Customers", scenario["customer_count"])
metrics[1].metric("Total demand", f"{total_demand} totes")
metrics[2].metric(
    "Fleet",
    f"{scenario['vehicle_count']} × {scenario['vehicle_capacity_totes']} totes",
)
metrics[3].metric("Fleet capacity", f"{fleet_capacity} totes")

metrics2 = st.columns(3)
metrics2[0].metric(
    "Theoretical minimum vans",
    precheck.get("minimum_vehicles_by_demand") or "—",
)
metrics2[1].metric("Demand / capacity", format_pct(ratio))
metrics2[2].metric("Distance source", scenario["distance_source"])
st.caption(payload.get("synthetic_distance_label", ""))

status_badge(precheck.get("status"))
st.markdown("**Feasibility pre-checks**")
check_rows = []
for check in precheck.get("checks", []):
    label = check["code"]
    if check["code"] == "CHECK_3":
        label = "CHECK_3 (informational)"
    check_rows.append(
        {
            "check": label,
            "name": check["name"],
            "passed": check["passed"],
            "hard_fail": check.get("hard_fail"),
            "message": check["message"],
        }
    )
st.dataframe(check_rows, use_container_width=True, hide_index=True)
st.caption("Check 3 is informational. A tight theoretical minimum is not a feasibility proof.")

if st.session_state.get("_validate_result"):
    with st.expander("Last validation response", expanded=False):
        st.json(st.session_state["_validate_result"])

st.markdown("**Customer demand**")
st.dataframe(
    [
        {
            "customer_id": customer["customer_id"],
            "zone_id": customer.get("zone_id"),
            "demand_totes": customer["demand_totes"],
            "latitude": customer.get("latitude"),
            "longitude": customer.get("longitude"),
        }
        for customer in customers
    ],
    use_container_width=True,
    hide_index=True,
)

if scenario.get("has_geographic_coordinates"):
    st.markdown("**Customer map**")
    st.plotly_chart(customer_map(payload), **PLOTLY_CHART_KWARGS)
    st.caption(
        "Customer locations are synthetic. Marker size follows tote demand. "
        "This is not a live operations map."
    )
elif scenario["scenario_id"] == "LEARNING_6":
    st.markdown("**Matrix-first view**")
    st.info(
        "LEARNING_6 has no geographic coordinates. Distances are shown from the "
        "backend matrix. No map is drawn."
    )
    st.dataframe(
        matrix_km_rows(payload["distance_matrix"]),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("This fixture has no geographic coordinates. No map is drawn.")

with st.expander("Full distance matrix (kilometres to 3 d.p.)"):
    st.dataframe(
        matrix_km_rows(payload["distance_matrix"]),
        use_container_width=True,
        hide_index=True,
    )

run_cols = st.columns(2)
with run_cols[0]:
    st.markdown("**Baseline run**")
    summary = summary_for_current("baseline")
    if summary:
        status_badge(summary.get("status"))
        st.write(f"Run: `{summary['run_id']}`")
        st.caption(f"Scenario: `{summary.get('scenario_id')}`")
        if summary.get("comparison_eligible"):
            st.write(f"Total distance: {format_km(summary.get('objective_distance_metres'))}")
        else:
            st.write("Total distance: —")
            if summary.get("partial_distance_metres") is not None:
                st.write(
                    "Partial constructed distance: "
                    f"{format_km(summary.get('partial_distance_metres'))}"
                )
        note = incomplete_baseline_note(summary)
        if note:
            st.info(note)
        else:
            st.write(summary.get("message") or "")
    else:
        st.caption("Not run for this scenario in this session.")
with run_cols[1]:
    st.markdown("**Optimised run**")
    summary = summary_for_current("optimised")
    if summary:
        status_badge(summary.get("status"))
        st.write(f"Run: `{summary['run_id']}`")
        st.caption(f"Scenario: `{summary.get('scenario_id')}`")
        st.write(f"Total distance: {format_km(summary.get('objective_distance_metres'))}")
        st.write(f"Solver termination: `{summary.get('solver_termination')}`")
        st.write(summary.get("message") or "")
    else:
        st.caption("Not run for this scenario in this session.")
