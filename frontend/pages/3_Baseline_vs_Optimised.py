"""Page 3: compare baseline and optimised API results."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from api_client import get_run
from components import (
    boot_page,
    call_api,
    empty_state,
    page_header,
    render_footer,
    section,
    static_table,
    status_badge,
)
from display import (
    format_improvement,
    format_km,
    format_pct,
    incomplete_baseline_note,
    operational_summary,
    status_label,
)
from i18n import t
from maps import PLOTLY_CHART_KWARGS
from state import summary_for_current

boot_page()

page_header(t("compare.title"), t("compare.subtitle"), kicker=t("compare.kicker"))

baseline_summary = summary_for_current("baseline")
optimised_summary = summary_for_current("optimised")
if not baseline_summary or not optimised_summary:
    empty_state(t("compare.empty.title"), t("compare.empty.body"))
    render_footer()
    st.stop()

baseline = call_api(get_run, baseline_summary["run_id"])
optimised = call_api(get_run, optimised_summary["run_id"])
if baseline is None or optimised is None:
    st.stop()

if baseline.get("scenario_id") != optimised.get("scenario_id"):
    st.error(t("compare.mismatch"))
    st.stop()

left, right = st.columns(2)
with left:
    st.subheader(t("compare.nn"))
    status_badge(baseline.get("status"))
    st.caption(t("compare.nn.cap"))
with right:
    st.subheader(t("compare.or"))
    status_badge(optimised.get("status"))
    st.caption(t("compare.or.cap"))

comparable = bool(baseline.get("comparison_eligible") and optimised.get("comparison_eligible"))
if not comparable:
    st.info(t("compare.need_both"))
note = incomplete_baseline_note(baseline)
if note:
    st.info(note)

section(t("compare.reading"))
st.markdown(operational_summary(baseline, optimised))
if comparable and baseline.get("scenario_id") != "LEARNING_6":
    st.caption(t("dispatch.not_optimal"))

section(t("compare.table"))
yes, no = t("common.yes"), t("common.no")
base_label = t("compare.nn")
opt_label = t("compare.or")
rows = [
    {
        t("compare.col.kpi"): t("compare.kpi.status"),
        base_label: status_label(baseline.get("status")),
        opt_label: status_label(optimised.get("status")),
    },
    {
        t("compare.col.kpi"): t("compare.kpi.eligible"),
        base_label: yes if baseline.get("comparison_eligible") else no,
        opt_label: yes if optimised.get("comparison_eligible") else no,
    },
    {
        t("compare.col.kpi"): t("compare.kpi.served"),
        base_label: f"{baseline['customers_served']} / {baseline['customers_total']}",
        opt_label: f"{optimised['customers_served']} / {optimised['customers_total']}",
    },
    {
        t("compare.col.kpi"): t("compare.kpi.demand"),
        base_label: baseline["demand_served_totes"],
        opt_label: optimised["demand_served_totes"],
    },
    {
        t("compare.col.kpi"): t("compare.kpi.vans"),
        base_label: baseline.get("vehicles_used"),
        opt_label: optimised.get("vehicles_used"),
    },
    {
        t("compare.col.kpi"): t("compare.kpi.total"),
        base_label: (
            format_km(baseline.get("objective_distance_metres"))
            if baseline.get("comparison_eligible")
            else t("common.na")
        ),
        opt_label: format_km(optimised.get("objective_distance_metres")),
    },
    {
        t("compare.col.kpi"): t("compare.kpi.partial"),
        base_label: format_km(baseline.get("partial_distance_metres")),
        opt_label: format_km(optimised.get("partial_distance_metres")),
    },
    {
        t("compare.col.kpi"): t("compare.kpi.util"),
        base_label: format_pct((baseline.get("kpis") or {}).get("used_fleet_utilisation")),
        opt_label: format_pct((optimised.get("kpis") or {}).get("used_fleet_utilisation")),
    },
    {
        t("compare.col.kpi"): t("compare.kpi.improve"),
        base_label: t("common.na"),
        opt_label: format_improvement(optimised.get("distance_improvement_percentage")),
    },
]
static_table(rows, row_header=t("compare.col.kpi"))
st.caption(t("compare.improve.cap"))

chart_layout = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "#F4F7FA",
    "font": {"color": "#172B3A", "family": "Inter, Segoe UI, sans-serif"},
    "legend": {"orientation": "h", "y": 1.12},
    "margin": {"t": 56, "b": 40, "l": 48, "r": 16},
    "height": 360,
}

if comparable:
    distance_fig = go.Figure(
        data=[
            go.Bar(
                name=t("compare.chart.distance"),
                x=[t("compare.nn"), t("compare.or")],
                y=[
                    baseline["objective_distance_metres"] / 1000,
                    optimised["objective_distance_metres"] / 1000,
                ],
                marker_color=["#0F2744", "#2E6B4F"],
                hovertemplate="%{x}: %{y:.3f} km<extra></extra>",
            )
        ]
    )
    distance_fig.update_layout(title=t("compare.chart.distance"), yaxis_title="km", **chart_layout)
    st.plotly_chart(distance_fig, **PLOTLY_CHART_KWARGS)
else:
    st.caption(t("compare.chart.skip"))

load_fig = go.Figure()
for label, payload, colour in (
    (t("compare.nn"), baseline, "#0F2744"),
    (t("compare.or"), optimised, "#2E6B4F"),
):
    vehicles = payload.get("vehicle_kpis") or []
    load_fig.add_trace(
        go.Bar(
            name=label,
            x=[item["vehicle_id"] for item in vehicles],
            y=[item["assigned_demand_totes"] for item in vehicles],
            marker_color=colour,
            hovertemplate="%{x}: %{y} totes<extra>" + label + "</extra>",
        )
    )
load_fig.update_layout(
    barmode="group",
    title=t("compare.chart.load"),
    yaxis_title=t("tote.word"),
    **chart_layout,
)
st.plotly_chart(load_fig, **PLOTLY_CHART_KWARGS)

route_fig = go.Figure()
for label, payload, colour in (
    (t("compare.nn"), baseline, "#0F2744"),
    (t("compare.or"), optimised, "#2E6B4F"),
):
    vehicles = payload.get("vehicle_kpis") or []
    route_fig.add_trace(
        go.Bar(
            name=label,
            x=[item["vehicle_id"] for item in vehicles],
            y=[item["route_distance_metres"] / 1000 for item in vehicles],
            marker_color=colour,
            hovertemplate="%{x}: %{y:.3f} km<extra>" + label + "</extra>",
        )
    )
route_fig.update_layout(
    barmode="group",
    title=t("compare.chart.route"),
    yaxis_title="km",
    **chart_layout,
)
st.plotly_chart(route_fig, **PLOTLY_CHART_KWARGS)

if baseline.get("status") == "heuristic_incomplete":
    st.warning(t("compare.warn.incomplete"))

st.page_link("pages/4_Model_Inspector.py", label=t("compare.next"), icon="🔎")
render_footer()
