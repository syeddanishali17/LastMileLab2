"""One result page: paired KPIs, both route maps, dispatch details and exports."""

import streamlit as st

from api_client import get_checks, get_routes, get_run, get_scenario
from components import (
    call_api,
    empty_state,
    export_buttons,
    kpi_cards,
    page_header,
    render_footer,
    section,
    static_table,
    status_badge,
)
from display import format_improvement, format_km, format_sequence, scenario_label, vehicle_colour
from i18n import t
from maps import PLOTLY_CHART_KWARGS, route_map
from state import summary_for_current

page_header(t("ux.plan.title"), t("ux.plan.subtitle"))
baseline = summary_for_current("baseline")
optimised = summary_for_current("optimised")
if baseline is None or optimised is None:
    empty_state(t("empty.plan.title"), t("ux.plan.empty"))
    render_footer()
    st.stop()

bundle = st.session_state.get("_plan_bundle")
if (
    bundle is None
    or bundle["baseline"]["run"]["run_id"] != baseline["run_id"]
    or bundle["optimised"]["run"]["run_id"] != optimised["run_id"]
):
    bundle = {"scenario": call_api(get_scenario, st.session_state.scenario_id)}
    for kind, summary in (("baseline", baseline), ("optimised", optimised)):
        run_id = summary["run_id"]
        bundle[kind] = {
            "run": call_api(get_run, run_id),
            "routes": call_api(get_routes, run_id),
            "checks": call_api(get_checks, run_id),
        }
    if bundle["scenario"] is None or any(
        value is None for kind in ("baseline", "optimised") for value in bundle[kind].values()
    ):
        st.stop()
    st.session_state["_plan_bundle"] = bundle

baseline = bundle["baseline"]["run"]
optimised = bundle["optimised"]["run"]
if baseline["scenario_id"] != optimised["scenario_id"]:
    st.error(t("compare.mismatch"))
    st.stop()

st.caption(scenario_label(st.session_state.scenario_id))
comparable = bool(baseline["comparison_eligible"] and optimised["comparison_eligible"])
section(t("ux.plan.summary"))
kpi_cards(
    [
        (
            t("ux.kpi.baseline"),
            format_km(baseline["objective_distance_metres"])
            if baseline["comparison_eligible"]
            else t("common.na"),
        ),
        (
            t("ux.kpi.optimised"),
            format_km(optimised["objective_distance_metres"])
            if optimised["comparison_eligible"]
            else t("common.na"),
        ),
        (
            t("ux.kpi.saving"),
            format_improvement(optimised["distance_improvement_percentage"])
            if comparable
            else t("common.na"),
        ),
        (
            t("ux.kpi.served"),
            f"{optimised['customers_served']} / {optimised['customers_total']}",
        ),
    ]
)
if not comparable:
    st.info(t("ux.plan.ineligible"))

st.caption(t("map.schematic"))
st.markdown(
    " · ".join(
        f'<span style="border-left:4px solid {vehicle_colour(v["vehicle_id"])};'
        f'padding-left:6px">{v["vehicle_id"]}</span>'
        for v in bundle["optimised"]["routes"]["vehicle_kpis"]
    ),
    unsafe_allow_html=True,
)
st.caption(t("ux.map.legend"))

figures = {
    kind: route_map(
        bundle["scenario"],
        bundle[kind]["routes"],
        unserved_ids=bundle[kind]["run"]["unserved_customer_ids"],
    )
    for kind in ("baseline", "optimised")
}


def total_distance_label(run: dict) -> str:
    if run["comparison_eligible"]:
        return t("ux.plan.total", km=format_km(run["objective_distance_metres"]))
    if run.get("partial_distance_metres") is not None:
        return t("ux.plan.partial", km=format_km(run["partial_distance_metres"]))
    return t("ux.plan.total", km=t("common.na"))


def route_table(routes: dict) -> None:
    static_table(
        [
            {
                t("ux.van"): vehicle["vehicle_id"],
                t("ux.load"): f"{vehicle['assigned_demand_totes']} / {vehicle['capacity_totes']}",
                t("ux.stops"): vehicle["customer_count"],
                t("ux.distance"): format_km(vehicle["route_distance_metres"]),
                t("ux.sequence"): format_sequence(vehicle["sequence"] or []),
            }
            for vehicle in routes["vehicle_kpis"]
        ],
        row_header=t("ux.van"),
        numeric_columns={t("ux.stops"), t("ux.distance"), t("ux.load")},
    )
    st.caption(t("ux.stops.help"))
    with st.expander(t("ux.plan.details")):
        static_table(
            [
                {
                    t("ux.van"): stop["vehicle_id"],
                    t("ux.stop"): stop["sequence_number"],
                    t("ux.customer"): stop["node_id"],
                    t("ux.totes"): stop["demand_totes"],
                    t("ux.leg"): format_km(stop["leg_distance_metres"]),
                    t("ux.cumulative"): stop["load_after_service_totes"],
                }
                for stop in routes["stops"]
            ],
            numeric_columns={t("ux.stop"), t("ux.totes"), t("ux.leg"), t("ux.cumulative")},
        )


with st.container(key="plan-pair"):
    left, right = st.columns(2, gap="large")
    for column, kind, heading in (
        (left, "baseline", t("ux.baseline")),
        (right, "optimised", t("ux.optimised")),
    ):
        with column:
            run = bundle[kind]["run"]
            st.markdown(f"**{heading}**")
            status_badge(run["status"], run_type=run["run_type"])
            if run["unserved_customer_ids"]:
                st.warning(t("ux.plan.unserved", ids=", ".join(run["unserved_customer_ids"])))
            st.plotly_chart(figures[kind], key=f"map-{kind}", **PLOTLY_CHART_KWARGS)
            st.markdown(f"**{total_distance_label(run)}**")
            if kind == "optimised" and comparable:
                st.caption(
                    t(
                        "ux.plan.reduction",
                        value=format_improvement(optimised["distance_improvement_percentage"]),
                    )
                )
            route_table(bundle[kind]["routes"])

section(t("ux.plan.exports"))
for column, kind, heading in zip(
    st.columns(2),
    ("baseline", "optimised"),
    (t("ux.baseline"), t("ux.optimised.short")),
    strict=True,
):
    with column:
        st.markdown(f"**{heading}**")
        export_buttons(bundle[kind]["run"]["run_id"], visible=True)
st.caption(t("ux.plan.excel"))

with st.expander(t("ux.plan.audit")):
    for kind, heading in (("baseline", t("ux.baseline")), ("optimised", t("ux.optimised.short"))):
        st.markdown(f"**{heading}**")
        checks = bundle[kind]["checks"]["checks"]
        for check in checks:
            st.write(("✓ " if check["passed"] else "✗ ") + t(f"check.audit.{check['code']}"))
        if any(not check["passed"] for check in checks):
            st.warning(t("ux.plan.audit.failed"))
    st.page_link("pages/4_Model_Inspector.py", label=t("nav.inspect"))
st.page_link("pages/6_Methodology.py", label=t("nav.method"))
render_footer()
