"""LastMile Lab: ViennaCart CVRP Dispatch Planner."""

from __future__ import annotations

import streamlit as st

from api_client import backend_url, get_health
from components import call_api, inject_theme, render_sidebar
from display import SYNTHETIC_NOTICE
from state import ensure_session

st.set_page_config(
    page_title="LastMile Lab: ViennaCart CVRP Dispatch Planner",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_session()
inject_theme()
render_sidebar()

st.title("LastMile Lab: ViennaCart CVRP Dispatch Planner")
st.caption("Static morning CVRP dispatch for the fictional ViennaCart operator.")

st.markdown(
    """
ViennaCart must assign every customer order to one van and sequence the stops
so that tote capacity is respected while total distance is minimised.

This application plans one frozen morning wave. It is not live traffic control.
    """
)

cols = st.columns(3)
with cols[0]:
    st.metric("Backend", backend_url())
with cols[1]:
    health = call_api(get_health)
    st.metric("API health", "offline" if health is None else health.get("status", "unknown"))
with cols[2]:
    st.metric("Active scenario", st.session_state.scenario_id)

if health is None:
    st.error(
        "The UI cannot reach FastAPI. Start the API on port 8000, then reload this page. "
        "Do not host this app on Streamlit Community Cloud; it cannot run the API."
    )

st.info(SYNTHETIC_NOTICE)

st.markdown(
    """
**How to use the planner**

1. Open **Dispatch Setup**, load a scenario, and inspect demand and capacity.
2. Run the nearest-neighbour baseline, then OR-Tools.
3. Review routes, the baseline-versus-optimised comparison, and the Model Inspector.
4. Use **Learning Lab** for the six-customer teaching fixture.

The Streamlit pages call FastAPI. They do not re-solve the CVRP.
    """
)
