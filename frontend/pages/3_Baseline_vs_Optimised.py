"""Page 3: compare baseline and optimised API results."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from api_client import get_run
from components import call_api, inject_theme, render_sidebar, status_badge
from display import (
    format_improvement,
    format_km,
    format_pct,
    incomplete_baseline_note,
    operational_summary,
)
from state import ensure_session, summary_for_current

ensure_session()
inject_theme()
render_sidebar()

st.title("Baseline vs Optimised")
st.caption("Comparison uses FastAPI KPI fields. Widgets do not recompute the objective.")

baseline_summary = summary_for_current("baseline")
optimised_summary = summary_for_current("optimised")
if not baseline_summary or not optimised_summary:
    st.warning("Run both the baseline and the optimiser on Dispatch Setup first.")
    st.stop()

baseline = call_api(get_run, baseline_summary["run_id"])
optimised = call_api(get_run, optimised_summary["run_id"])
if baseline is None or optimised is None:
    st.stop()

if baseline.get("scenario_id") != optimised.get("scenario_id"):
    st.error(
        "Baseline and optimiser runs belong to different scenarios. "
        "Load one scenario, then run both planners on it."
    )
    st.stop()

left, right = st.columns(2)
with left:
    st.subheader("Nearest neighbour")
    status_badge(baseline.get("status"))
with right:
    st.subheader("OR-Tools")
    status_badge(optimised.get("status"))

comparable = bool(baseline.get("comparison_eligible") and optimised.get("comparison_eligible"))
if not comparable:
    st.info(
        "Total-distance comparison is shown only when both runs are comparison-eligible. "
        "An incomplete baseline does not receive an invented complete distance."
    )
note = incomplete_baseline_note(baseline)
if note:
    st.info(note)

st.markdown(operational_summary(baseline, optimised))

rows = [
    {
        "KPI": "Status",
        "Baseline": baseline.get("status"),
        "Optimised": optimised.get("status"),
    },
    {
        "KPI": "Comparison eligible",
        "Baseline": str(baseline.get("comparison_eligible")),
        "Optimised": str(optimised.get("comparison_eligible")),
    },
    {
        "KPI": "Customers served",
        "Baseline": f"{baseline['customers_served']} / {baseline['customers_total']}",
        "Optimised": f"{optimised['customers_served']} / {optimised['customers_total']}",
    },
    {
        "KPI": "Demand served (totes)",
        "Baseline": baseline["demand_served_totes"],
        "Optimised": optimised["demand_served_totes"],
    },
    {
        "KPI": "Vehicles used",
        "Baseline": baseline.get("vehicles_used"),
        "Optimised": optimised.get("vehicles_used"),
    },
    {
        "KPI": "Total distance",
        "Baseline": (
            format_km(baseline.get("objective_distance_metres"))
            if baseline.get("comparison_eligible")
            else "—"
        ),
        "Optimised": format_km(optimised.get("objective_distance_metres")),
    },
    {
        "KPI": "Partial constructed distance",
        "Baseline": format_km(baseline.get("partial_distance_metres")),
        "Optimised": format_km(optimised.get("partial_distance_metres")),
    },
    {
        "KPI": "Used-fleet utilisation",
        "Baseline": format_pct((baseline.get("kpis") or {}).get("used_fleet_utilisation")),
        "Optimised": format_pct((optimised.get("kpis") or {}).get("used_fleet_utilisation")),
    },
    {
        "KPI": "Distance improvement",
        "Baseline": "—",
        "Optimised": format_improvement(optimised.get("distance_improvement_percentage")),
    },
]
st.dataframe(rows, use_container_width=True, hide_index=True)

if comparable:
    distance_fig = go.Figure(
        data=[
            go.Bar(
                name="Total distance (km)",
                x=["Baseline", "Optimised"],
                y=[
                    baseline["objective_distance_metres"] / 1000,
                    optimised["objective_distance_metres"] / 1000,
                ],
                marker_color=["#1f4e79", "#2e7d4f"],
            )
        ]
    )
    distance_fig.update_layout(
        title="Total distance",
        yaxis_title="km",
        height=360,
        margin={"t": 40, "b": 40},
    )
    st.plotly_chart(distance_fig, use_container_width=True)
else:
    st.caption(
        "The total-distance chart is omitted because the baseline "
        "is not comparison-eligible."
    )

load_fig = go.Figure()
for label, payload, colour in (
    ("Baseline", baseline, "#1f4e79"),
    ("Optimised", optimised, "#2e7d4f"),
):
    vehicles = payload.get("vehicle_kpis") or []
    load_fig.add_trace(
        go.Bar(
            name=label,
            x=[item["vehicle_id"] for item in vehicles],
            y=[item["assigned_demand_totes"] for item in vehicles],
            marker_color=colour,
        )
    )
load_fig.update_layout(barmode="group", title="Assigned load by van (totes)", height=360)
st.plotly_chart(load_fig, use_container_width=True)

route_fig = go.Figure()
for label, payload, colour in (
    ("Baseline", baseline, "#1f4e79"),
    ("Optimised", optimised, "#2e7d4f"),
):
    vehicles = payload.get("vehicle_kpis") or []
    route_fig.add_trace(
        go.Bar(
            name=label,
            x=[item["vehicle_id"] for item in vehicles],
            y=[item["route_distance_metres"] / 1000 for item in vehicles],
            marker_color=colour,
        )
    )
route_fig.update_layout(barmode="group", title="Route distance by van (km)", height=360)
st.plotly_chart(route_fig, use_container_width=True)

if baseline.get("status") == "heuristic_incomplete":
    st.warning(
        "Sequential nearest neighbour left customers unserved. The optimiser result "
        "is still shown. Do not read the baseline partial kilometres as a complete plan."
    )
