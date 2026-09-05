"""Scenario selection, guided demand editing, and a single comparison action."""

import streamlit as st

from api_client import (
    ApiError,
    generate_scenario,
    get_checks,
    get_routes,
    get_run,
    get_scenario,
    run_baseline,
    run_optimise,
)
from components import call_api, page_header, render_footer, search_pulse, section
from display import scenario_help, scenario_label
from i18n import t
from maps import PLOTLY_CHART_KWARGS, customer_map
from scenario_builder import capacity_preview
from state import clear_planner_runs, set_scenario

PRESETS = ["VIENNA_STANDARD_24", "VIENNA_TIGHT_24", "VIENNA_WIDE_24"]


def show_capacity(preview: dict, capacity: int) -> None:
    if not preview["valid"]:
        st.error(t("ux.check.invalid"))
        return
    order, fleet = st.columns(2)
    with order:
        st.progress(
            min(preview["largest"] / capacity, 1.0),
            text=f"{t('ux.check.order')}: {preview['largest']} / {capacity}",
        )
        if not preview["order_ok"]:
            st.error(t("ux.check.oversize"))
    with fleet:
        st.progress(
            min(preview["total"] / preview["fleet"], 1.0),
            text=f"{t('ux.check.fleet')}: {preview['total']} / {preview['fleet']}",
        )
        if not preview["fleet_ok"]:
            st.error(t("ux.check.overflow"))
    spare, minimum = st.columns(2)
    spare.metric(t("ux.check.spare"), preview["spare"])
    minimum.metric(
        t("ux.check.min"),
        preview["minimum_vans"],
        help=t("tip.minvans"),
    )
    st.caption(t("ux.check.packing"))


def compare(scenario_id: str, seconds: int) -> bool:
    # Publish the pair to session state only after both responses and audit data arrive.
    clear_planner_runs()
    with st.status(t("ux.stage.load"), expanded=True) as status:
        try:
            scenario = get_scenario(scenario_id)
            st.write(t("ux.stage.load") + " ✓")
            status.update(label=t("ux.stage.baseline"))
            baseline = run_baseline(scenario_id)
            st.write(t("ux.stage.baseline") + " ✓")
            status.update(label=t("ux.stage.optimise", n=seconds))
            search_pulse()
            st.write(t("ux.stage.optimise", n=seconds))
            optimised = run_optimise(scenario_id, seconds)
            status.update(label=t("ux.stage.reconcile"))
            bundle = {"scenario": scenario}
            for kind, result in (("baseline", baseline), ("optimised", optimised)):
                run_id = result["run_id"]
                bundle[kind] = {
                    "run": get_run(run_id),
                    "routes": get_routes(run_id),
                    "checks": get_checks(run_id),
                }
            status.update(label=t("ux.stage.prepare"))
            st.session_state["_plan_bundle"] = bundle
            for kind, result in (("baseline", baseline), ("optimised", optimised)):
                st.session_state[f"{kind}_run_id"] = result["run_id"]
                st.session_state[f"_{kind}_summary"] = bundle[kind]["run"]
            status.update(label=t("ux.stage.done"), state="complete", expanded=False)
            return True
        except ApiError as exc:
            status.update(label=t("ux.stage.failed"), state="error", expanded=True)
            st.error(t("ux.error"))
            st.caption(str(exc))
            return False


page_header(t("ux.scenarios.title"), t("ux.scenarios.subtitle"))
source_default = "custom" if st.session_state.scenario_id.startswith("GEN_") else "presets"
source = st.radio(
    t("ux.source"),
    ("presets", "custom"),
    index=0 if source_default == "presets" else 1,
    format_func=lambda value: t(f"ux.{value}"),
    horizontal=True,
    key="scenario_source",
)
payload = None
ready = False
inputs, preview_panel = st.columns([1, 1.15], gap="large")
with inputs:
    if source == "presets":
        current = st.session_state.scenario_id
        selected = st.radio(
            t("ux.presets"),
            PRESETS,
            index=PRESETS.index(current) if current in PRESETS else 0,
            format_func=scenario_label,
            captions=[scenario_help(preset) for preset in PRESETS],
        )
        set_scenario(selected)
        payload = call_api(get_scenario, selected)
        ready = payload is not None and payload["precheck"]["status"] == "passed"
        if payload is not None:
            demands = [customer["demand_totes"] for customer in payload["customers"]]
            show_capacity(
                capacity_preview(
                    demands,
                    payload["scenario"]["vehicle_count"],
                    payload["scenario"]["vehicle_capacity_totes"],
                ),
                payload["scenario"]["vehicle_capacity_totes"],
            )
    else:
        st.write(t("ux.custom.help"))
        config = st.session_state.get("_custom_config", {"n": 24, "vans": 4, "capacity": 30})
        left, middle, right = st.columns(3)
        n = int(left.number_input(t("ux.custom.count"), 1, 50, config["n"], key="custom_n"))
        vans = int(
            middle.number_input(t("ux.custom.vans"), 1, 10, config["vans"], key="custom_vans")
        )
        capacity = int(
            right.number_input(
                t("ux.custom.capacity"),
                1,
                100,
                config["capacity"],
                key="custom_capacity",
            )
        )
        st.session_state["_custom_config"] = {"n": n, "vans": vans, "capacity": capacity}
        section(t("ux.custom.orders"))
        editor_key = f"demand_editor_{n}"
        if editor_key not in st.session_state:
            previous = st.session_state.get("_custom_demands", [])
            values = previous if len(previous) == n else [(4, 5, 6, 3)[i % 4] for i in range(n)]
            st.session_state["_editor_base"] = [
                {"customer": f"C{i + 1:03d}", "totes": value} for i, value in enumerate(values)
            ]
        rows = st.data_editor(
            st.session_state["_editor_base"],
            key=editor_key,
            disabled=["customer"],
            hide_index=True,
            num_rows="fixed",
            use_container_width=True,
            height=245,
            column_config={
                "customer": st.column_config.TextColumn(t("ux.customer")),
                "totes": st.column_config.NumberColumn(
                    t("ux.totes"), min_value=1, max_value=100, step=1
                ),
            },
        )
        demands = [row["totes"] for row in rows]
        st.session_state["_custom_demands"] = demands
        preview = capacity_preview(demands, vans, capacity)
        show_capacity(preview, capacity)
        settings = st.session_state.get("_custom_location", {"seed": 42, "detour": 1.25})
        with st.expander(t("ux.custom.advanced")):
            seed = int(st.number_input(t("ux.seed"), 0, 2147483647, settings["seed"]))
            detour = st.number_input(
                t("ux.detour"),
                1.0,
                2.0,
                settings["detour"],
                step=0.05,
                help=t("tip.detour"),
            )
        st.session_state["_custom_location"] = {"seed": seed, "detour": detour}
        request = {
            "random_seed": seed,
            "customer_count": n,
            "vehicle_count": vans,
            "vehicle_capacity_totes": capacity,
            "detour_factor": round(detour, 2),
            "geographic_zone_weights": {"Z1": 0.25, "Z2": 0.25, "Z3": 0.25, "Z4": 0.25},
            "customer_demands": demands,
        }
        if st.button(t("ux.generate"), disabled=not preview["can_generate"], type="secondary"):
            generated = call_api(generate_scenario, request)
            if generated is not None:
                set_scenario(generated["scenario_id"])
                st.session_state["_generated_request"] = request
                st.session_state["_generated_payload"] = call_api(
                    get_scenario, generated["scenario_id"]
                )
        ready = (
            preview["can_generate"]
            and request == st.session_state.get("_generated_request")
            and st.session_state.get("_generated_payload") is not None
        )
        if ready:
            payload = st.session_state["_generated_payload"]
            set_scenario(payload["scenario"]["scenario_id"])
            st.success(t("ux.custom.ready"))
        else:
            st.info(t("ux.custom.changed"))

    seconds = st.radio(
        t("ux.seconds"),
        [1, 5, 10],
        horizontal=True,
        index=[1, 5, 10].index(st.session_state.solver_time_limit_seconds),
        key="_search_seconds",
        help=t("tip.search"),
    )
    st.session_state.solver_time_limit_seconds = seconds
    if st.button(t("ux.run"), type="primary", disabled=not ready):
        if compare(st.session_state.scenario_id, st.session_state.solver_time_limit_seconds):
            st.switch_page("pages/3_Baseline_vs_Optimised.py")

with preview_panel:
    if payload is not None:
        scenario = payload["scenario"]
        demands = [customer["demand_totes"] for customer in payload["customers"]]
        section(
            t("ux.preview"),
            t(
                "ux.preview.summary",
                n=scenario["customer_count"],
                demand=sum(demands),
                vans=scenario["vehicle_count"],
                capacity=scenario["vehicle_capacity_totes"],
            ),
        )
        st.plotly_chart(customer_map(payload), key="scenario-map", **PLOTLY_CHART_KWARGS)
        with st.expander(t("ux.custom.orders")):
            st.dataframe(
                [
                    {
                        t("ux.customer"): customer["customer_id"],
                        t("ux.totes"): customer["demand_totes"],
                    }
                    for customer in payload["customers"]
                ],
                hide_index=True,
                use_container_width=True,
            )

    else:
        st.info(t("ux.preview.empty"))

render_footer()
