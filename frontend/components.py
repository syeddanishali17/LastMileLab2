"""Shared Streamlit layout. Display only; no solver or KPI formulae."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import streamlit as st

from api_client import ApiError, backend_url, get_health
from display import SYNTHETIC_NOTICE, format_km, format_pct, format_sequence, vehicle_colour
from state import ensure_session


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.4rem; max-width: 1400px; }
        div[data-testid="stMetricValue"] { font-size: 1.15rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    ensure_session()
    with st.sidebar:
        st.markdown("**LastMile Lab**")
        st.caption("ViennaCart CVRP Dispatch Planner")
        try:
            health = get_health()
            st.success(f"API {health.get('status', 'ok')}")
        except ApiError:
            st.error("API offline")
        st.caption(backend_url())
        st.divider()
        st.write(f"Scenario: `{st.session_state.scenario_id}`")
        st.write(f"Baseline: `{st.session_state.baseline_run_id or '—'}`")
        st.write(f"Optimised: `{st.session_state.optimised_run_id or '—'}`")
        st.divider()
        st.caption(SYNTHETIC_NOTICE)


def call_api(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    try:
        return func(*args, **kwargs)
    except ApiError as exc:
        if exc.kind == "connection":
            st.error(str(exc))
            st.caption(
                "In PowerShell: "
                r".\.venv\Scripts\python.exe -m uvicorn app.main:app "
                "--app-dir backend --host 127.0.0.1 --port 8000"
            )
        elif exc.kind == "timeout":
            st.warning(str(exc))
        elif exc.kind == "not_found":
            st.error(str(exc))
            st.caption("Load the scenario again after restarting the API.")
        elif exc.kind == "server":
            st.error("The planner hit an unexpected server error. The API is running.")
            st.caption(str(exc))
        else:
            st.error(str(exc))
        return None


def export_buttons(run_id: str) -> None:
    from api_client import export_run

    with st.expander("Export this run"):
        col_json, col_csv = st.columns(2)
        with col_json:
            payload = call_api(export_run, run_id, "json")
            if payload is not None:
                content, mime, name = payload
                st.download_button(
                    "Download JSON",
                    data=content,
                    file_name=name,
                    mime=mime,
                    key=f"export-json-{run_id}",
                )
        with col_csv:
            payload = call_api(export_run, run_id, "csv")
            if payload is not None:
                content, mime, name = payload
                st.download_button(
                    "Download CSV zip",
                    data=content,
                    file_name=name,
                    mime=mime,
                    key=f"export-csv-{run_id}",
                )


def status_badge(status: str | None) -> None:
    if not status:
        st.info("No run yet")
        return
    palette = {
        "feasible": st.success,
        "heuristic_incomplete": st.warning,
        "no_solution_found": st.warning,
        "infeasible": st.error,
        "invalid": st.error,
        "error": st.error,
        "pending": st.info,
        "passed": st.success,
    }
    writer = palette.get(status, st.info)
    writer(f"Status: `{status}`")


def vehicle_card(vehicle: dict[str, Any]) -> None:
    colour = vehicle_colour(vehicle["vehicle_id"])
    utilisation = vehicle.get("capacity_utilisation")
    used = vehicle.get("is_used")
    title = f"Van {vehicle['vehicle_id']}"
    if not used:
        title += " — unused"
    st.markdown(
        f"<div style='border-left:6px solid {colour};padding-left:0.75rem'>",
        unsafe_allow_html=True,
    )
    st.subheader(title)
    if used and vehicle.get("sequence"):
        st.write(f"Route: {format_sequence(vehicle['sequence'])}")
        st.write(f"Orders: {vehicle['customer_count']}")
        st.write(
            f"Load: {vehicle['assigned_demand_totes']} / {vehicle['capacity_totes']} totes"
        )
        st.write(f"Capacity utilisation: {format_pct(utilisation)}")
        st.write(f"Distance: {format_km(vehicle.get('route_distance_metres'))}")
        st.progress(min(float(utilisation or 0.0), 1.0))
    else:
        st.caption("This van was not used.")
        st.write(f"Capacity: {vehicle['capacity_totes']} totes")
    st.markdown("</div>", unsafe_allow_html=True)
