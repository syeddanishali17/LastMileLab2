"""Streamlit session keys. No planning logic lives here."""

from __future__ import annotations

from typing import Any

import streamlit as st

SESSION_DEFAULTS = {
    "scenario_id": "VIENNA_STANDARD_24",
    "baseline_run_id": None,
    "optimised_run_id": None,
    "solver_time_limit_seconds": 5,
    "learning_baseline_run_id": None,
    "learning_optimised_run_id": None,
    "ui_language": "en",
    "plan_view": "comparison",
    "_baseline_summary": None,
    "_optimised_summary": None,
}

# Durable copy of the language choice. Streamlit can remount the sidebar radio
# with its default value after st.switch_page(); this key is not widget-owned.
LANGUAGE_PERSIST_KEY = "ui_language_persist"
VALID_LANGUAGES = ("en", "de")

# Comparison/run keys dropped or reset by clear_planner_runs(). Language, scenario_id,
# solver limit, custom-scenario config, and _planning_offline are left unchanged.
PLANNER_RUN_KEYS = (
    "_plan_bundle",
    "baseline_run_id",
    "optimised_run_id",
    "_baseline_summary",
    "_optimised_summary",
    "_export_payloads",
)


def restore_language() -> None:
    persist = st.session_state.get(LANGUAGE_PERSIST_KEY)
    current = st.session_state.get("ui_language")
    if persist in VALID_LANGUAGES:
        st.session_state.ui_language = persist
    elif current in VALID_LANGUAGES:
        st.session_state[LANGUAGE_PERSIST_KEY] = current


def persist_language() -> None:
    lang = st.session_state.get("ui_language")
    if lang in VALID_LANGUAGES:
        st.session_state[LANGUAGE_PERSIST_KEY] = lang


def ensure_session() -> None:
    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value
    restore_language()
    drop_stale_runs()


def clear_planner_runs() -> None:
    """Drop stored comparison results after a scenario change or expired run.

    Clears: `_plan_bundle`, `baseline_run_id`, `optimised_run_id`,
    `_baseline_summary`, `_optimised_summary`, `_export_payloads`.
    Resets `plan_view` to comparison. Does not reset language or scenario setup.
    """
    st.session_state.pop("_plan_bundle", None)
    st.session_state.pop("_export_payloads", None)
    st.session_state.plan_view = "comparison"
    st.session_state.baseline_run_id = None
    st.session_state.optimised_run_id = None
    st.session_state["_baseline_summary"] = None
    st.session_state["_optimised_summary"] = None


def set_scenario(scenario_id: str) -> None:
    if st.session_state.get("scenario_id") != scenario_id:
        clear_planner_runs()
    st.session_state.scenario_id = scenario_id


def drop_stale_runs() -> None:
    current = st.session_state.get("scenario_id")
    baseline = st.session_state.get("_baseline_summary")
    if baseline and baseline.get("scenario_id") != current:
        st.session_state.baseline_run_id = None
        st.session_state["_baseline_summary"] = None
    optimised = st.session_state.get("_optimised_summary")
    if optimised and optimised.get("scenario_id") != current:
        st.session_state.optimised_run_id = None
        st.session_state["_optimised_summary"] = None


def summary_for_current(kind: str) -> dict[str, Any] | None:
    summary = st.session_state.get(f"_{kind}_summary")
    if summary and summary.get("scenario_id") == st.session_state.scenario_id:
        return summary
    return None
