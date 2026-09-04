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
    distance_source_label,
    format_km,
    format_pct,
    incomplete_baseline_note,
    matrix_km_rows,
    scenario_help,
    scenario_label,
)
from i18n import t
from maps import PLOTLY_CHART_KWARGS, customer_map
from state import set_scenario, summary_for_current

boot_page()

page_header(t("dispatch.title"), t("dispatch.subtitle"), kicker=t("dispatch.kicker"))

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

section(t("dispatch.pick"), t("dispatch.pick.cap"))
selected = st.selectbox(
    t("dispatch.pick"),
    options=choices,
    index=choices.index(current) if current in choices else 0,
    format_func=scenario_label,
    help=t("dispatch.pick.help"),
)
st.caption(scenario_help(selected))
if selected != st.session_state.scenario_id:
    st.warning(t("dispatch.need_load"))

col_a, col_b = st.columns(2)
with col_a:
    load_clicked = st.button(
        t("dispatch.load"),
        type="primary" if selected != st.session_state.scenario_id else "secondary",
        help=t("dispatch.load.help"),
        use_container_width=True,
    )
with col_b:
    validate_clicked = st.button(
        t("dispatch.validate"),
        help=t("dispatch.validate.help"),
        use_container_width=True,
    )

section(t("dispatch.solve"), t("dispatch.solve.cap"))
if st.session_state.solver_time_limit_seconds not in (1, 5, 10):
    st.session_state.solver_time_limit_seconds = 5
with st.expander(t("dispatch.settings")):
    st.selectbox(
        t("dispatch.time"),
        options=[1, 5, 10],
        key="solver_time_limit_seconds",
        format_func=lambda seconds: t(f"dispatch.time.{seconds}"),
        help=t("dispatch.time.help"),
    )

col_c, col_d = st.columns(2)
scenario_not_active = selected != st.session_state.scenario_id
with col_c:
    baseline_clicked = st.button(
        t("dispatch.baseline"),
        help=t("dispatch.baseline.help"),
        disabled=scenario_not_active,
        use_container_width=True,
    )
with col_d:
    optimise_clicked = st.button(
        t("dispatch.optimise"),
        type="primary",
        help=t("dispatch.optimise.help"),
        disabled=scenario_not_active,
        use_container_width=True,
    )

if load_clicked:
    payload = call_api(get_scenario, selected)
    if payload is not None:
        set_scenario(selected)
        st.session_state["_scenario_payload"] = payload
        st.success(t("dispatch.loaded", id=selected))

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

with st.expander(t("dispatch.gen")):
    st.caption(t("dispatch.gen.cap"))
    seed = st.number_input(
        t("dispatch.gen.seed"),
        min_value=0,
        max_value=2147483647,
        value=42,
        step=1,
        help=t("dispatch.gen.seed.help"),
    )
    n_customers = st.number_input(
        t("dispatch.gen.customers"),
        min_value=1,
        max_value=50,
        value=24,
        step=1,
    )
    n_vehicles = st.number_input(
        t("dispatch.gen.vans"),
        min_value=1,
        max_value=10,
        value=4,
        step=1,
    )
    capacity = st.number_input(
        t("dispatch.gen.capacity"),
        min_value=1,
        max_value=100,
        value=30,
        step=1,
        help=t("dispatch.gen.capacity.help"),
    )
    detour = st.number_input(
        t("dispatch.gen.detour"),
        min_value=1.00,
        max_value=2.00,
        value=1.25,
        step=0.01,
        help=t("dispatch.gen.detour.help"),
    )
    z1 = st.number_input(
        t("dispatch.gen.z1"),
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.01,
        help=t("dispatch.gen.zone.help"),
    )
    z2 = st.number_input(
        t("dispatch.gen.z2"),
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.01,
        help=t("dispatch.gen.zone.help"),
    )
    z3 = st.number_input(
        t("dispatch.gen.z3"),
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.01,
        help=t("dispatch.gen.zone.help"),
    )
    z4 = st.number_input(
        t("dispatch.gen.z4"),
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.01,
        help=t("dispatch.gen.zone.help"),
    )
    if st.button(t("dispatch.gen.button"), help=t("dispatch.gen.button.help")):
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
            st.success(t("dispatch.gen.ok", id=generated["scenario_id"]))
            st.rerun()

if payload is None:
    st.stop()

scenario = payload["scenario"]
customers = payload["customers"]
precheck = payload["precheck"]
total_demand = sum(customer["demand_totes"] for customer in customers)
fleet_capacity = scenario["vehicle_count"] * scenario["vehicle_capacity_totes"]
ratio = total_demand / fleet_capacity if fleet_capacity else None

section(t("dispatch.demand"), t("dispatch.demand.cap"))
metrics = st.columns(4)
metrics[0].metric(
    t("dispatch.m.customers"),
    scenario["customer_count"],
    help=t("dispatch.m.customers.help"),
)
metrics[1].metric(
    t("dispatch.m.demand"),
    t("unit.totes", n=total_demand),
    help=t("tote.help"),
)
metrics[2].metric(
    t("dispatch.m.fleet"),
    t(
        "unit.fleet",
        vans=scenario["vehicle_count"],
        cap=scenario["vehicle_capacity_totes"],
    ),
    help=t("dispatch.m.fleet.help"),
)
metrics[3].metric(
    t("dispatch.m.capacity"),
    t("unit.totes", n=fleet_capacity),
    help=t("dispatch.m.capacity.help"),
)

metrics2 = st.columns(3)
metrics2[0].metric(
    t("dispatch.m.minvans"),
    precheck.get("minimum_vehicles_by_demand") or t("common.na"),
    help=t("dispatch.m.minvans.help"),
)
metrics2[1].metric(
    t("dispatch.m.ratio"),
    format_pct(ratio),
    help=t("dispatch.m.ratio.help"),
)
metrics2[2].metric(
    t("dispatch.m.source"),
    distance_source_label(scenario["distance_source"]),
    help=t("dispatch.m.source.help"),
)
st.caption(payload.get("synthetic_distance_label", ""))

section(t("dispatch.checks"), t("dispatch.checks.cap"))
status_badge(precheck.get("status"))
render_check_table(precheck.get("checks", []))
st.caption(t("dispatch.checks.note"))

if st.session_state.get("_validate_result"):
    with st.expander(t("dispatch.last_validate"), expanded=False):
        st.json(st.session_state["_validate_result"])

section(t("dispatch.orders"))
order_rows = [
    {
        t("dispatch.col.customer"): customer["customer_id"],
        t("dispatch.col.zone"): customer.get("zone_id"),
        t("dispatch.col.demand"): customer["demand_totes"],
        t("dispatch.col.lat"): customer.get("latitude"),
        t("dispatch.col.lon"): customer.get("longitude"),
    }
    for customer in customers
]
static_table(
    order_rows,
    row_header=t("dispatch.col.customer"),
)

if scenario.get("has_geographic_coordinates"):
    section(t("dispatch.map"), t("dispatch.map.cap"))
    st.plotly_chart(customer_map(payload), **PLOTLY_CHART_KWARGS)
    st.caption(t("map.schematic"))
elif scenario["scenario_id"] == "LEARNING_6":
    section(t("dispatch.matrix"), t("dispatch.matrix.cap"))
    callout(t("scenario.LEARNING_6.help"))
    learning_matrix_rows = matrix_km_rows(payload["distance_matrix"])
    from_label = t("inspect.col.from")
    static_table(
        learning_matrix_rows,
        numeric_columns=set(learning_matrix_rows[0]) - {from_label},
        row_header=from_label,
    )
else:
    st.info(t("dispatch.nogeo"))

with st.expander(t("dispatch.matrix.full")):
    st.caption(t("dispatch.matrix.full.cap"))
    st.dataframe(
        matrix_km_rows(payload["distance_matrix"]),
        use_container_width=True,
        hide_index=True,
    )

section(t("dispatch.runs"), t("dispatch.runs.cap"))
run_cols = st.columns(2)
with run_cols[0]:
    st.markdown(f"**{t('dispatch.simple')}**")
    summary = summary_for_current("baseline")
    if summary:
        status_badge(summary.get("status"))
        st.write(t("dispatch.run", id=summary["run_id"]))
        st.caption(f"{t('nav.scenario')}: `{summary.get('scenario_id')}`")
        if summary.get("comparison_eligible"):
            st.write(t("dispatch.total", km=format_km(summary.get("objective_distance_metres"))))
        else:
            st.write(t("dispatch.total", km=t("common.na")))
            if summary.get("partial_distance_metres") is not None:
                st.write(
                    t(
                        "dispatch.partial",
                        km=format_km(summary.get("partial_distance_metres")),
                    )
                )
        note = incomplete_baseline_note(summary)
        if note:
            st.info(note)
        else:
            st.write(summary.get("message") or "")
    else:
        st.caption(t("dispatch.norun"))
with run_cols[1]:
    st.markdown(f"**{t('dispatch.or')}**")
    summary = summary_for_current("optimised")
    if summary:
        status_badge(summary.get("status"))
        st.write(t("dispatch.run", id=summary["run_id"]))
        st.caption(f"{t('nav.scenario')}: `{summary.get('scenario_id')}`")
        st.write(t("dispatch.total", km=format_km(summary.get("objective_distance_metres"))))
        st.write(t("dispatch.term", term=summary.get("solver_termination")))
        st.write(summary.get("message") or "")
        if summary.get("comparison_eligible") and summary.get("scenario_id") != "LEARNING_6":
            st.caption(t("dispatch.not_optimal"))
    else:
        st.caption(t("dispatch.norun"))

nav_a, nav_b = st.columns(2)
with nav_a:
    st.page_link("pages/2_Route_Plan.py", label=t("dispatch.next.routes"), icon="🗺️")
with nav_b:
    st.page_link(
        "pages/3_Baseline_vs_Optimised.py",
        label=t("dispatch.next.compare"),
        icon="📊",
    )

render_footer()
