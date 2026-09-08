"""Scenario selection, guided demand editing, and a single comparison action."""

from html import escape

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
from components import (
    call_api,
    comparison_ready,
    fetch_preset_scenario,
    page_header,
    planning_offline_notice,
    render_footer,
    search_pulse,
)
from display import scenario_caption, scenario_label
from i18n import t
from maps import PLOTLY_CHART_KWARGS, customer_map
from scenario_builder import capacity_preview
from state import clear_planner_runs, set_scenario

PRESETS = ["VIENNA_STANDARD_24", "VIENNA_TIGHT_24", "VIENNA_WIDE_24"]
CUSTOM_DEFAULTS = {"n": 24, "vans": 4, "capacity": 30}
CUSTOM_LOCATION = {"seed": 42, "detour": 1.25}


def _heading(title: str) -> None:
    st.markdown(
        f'<div class="lm-section"><h2>{escape(title)}</h2></div>',
        unsafe_allow_html=True,
    )


def _default_demands(n: int) -> list[int]:
    return [(4, 5, 6, 3)[i % 4] for i in range(n)]


def _banner(kind: str, title: str, body: str | None = None) -> None:
    extra = f"<p>{escape(body)}</p>" if body else ""
    st.markdown(
        f'<div class="lm-{kind}"><p class="lm-{kind}-title">{escape(title)}</p>{extra}</div>',
        unsafe_allow_html=True,
    )


def _meter(ratio: float) -> str:
    width = max(0, min(ratio, 1.0)) * 100
    return (
        f'<div class="lm-feas-bar" aria-hidden="true">'
        f'<span style="width:{width:.1f}%"></span></div>'
    )


def _check_card(
    *,
    title: str,
    tip: str,
    lines: list[str],
    passed: bool | None,
    ratio: float | None = None,
) -> str:
    if passed is None:
        status = ""
        state = "is-info"
    elif passed:
        status = f'<p class="lm-feas-status">{escape(t("ux.check.pass"))}</p>'
        state = "is-pass"
    else:
        status = f'<p class="lm-feas-status">{escape(t("ux.check.fail"))}</p>'
        state = "is-fail"
    details = "".join(f"<p>{escape(line)}</p>" for line in lines)
    bar = _meter(ratio) if ratio is not None else ""
    heading = (
        f'<abbr class="lm-tip" title="{escape(tip)}">{escape(title)}</abbr>'
        if tip
        else escape(title)
    )
    return (
        f'<article class="lm-feas-card {state}">'
        f'<p class="lm-feas-title">{heading}</p>{status}{details}{bar}</article>'
    )


def show_capacity(preview: dict, vans: int, capacity: int) -> None:
    if not preview["valid"]:
        st.error(t("ux.check.invalid"))
        return
    min_ok = vans >= preview["minimum_vans"]
    cards = [
        _check_card(
            title=t("ux.check.order.title"),
            tip=t("ux.check.order.tip"),
            lines=[
                t("ux.check.order.largest", n=preview["largest"]),
                t("ux.check.order.capacity", n=capacity),
            ],
            passed=preview["order_ok"],
            ratio=preview["largest"] / capacity if capacity else 1,
        ),
        _check_card(
            title=t("ux.check.fleet.title"),
            tip=t("ux.check.fleet.tip"),
            lines=[
                t("ux.check.fleet.demand", n=preview["total"]),
                t("ux.check.fleet.capacity", n=preview["fleet"]),
            ],
            passed=preview["fleet_ok"],
            ratio=preview["total"] / preview["fleet"] if preview["fleet"] else 1,
        ),
        _check_card(
            title=t("ux.check.min"),
            tip=t("ux.check.min.help"),
            lines=[
                t("ux.check.min.required", n=preview["minimum_vans"]),
                t("ux.check.min.available", n=vans),
            ],
            passed=min_ok,
        ),
        _check_card(
            title=t("ux.check.spare"),
            tip="",
            lines=[t("ux.check.spare.value", n=preview["spare"])],
            passed=None,
        ),
    ]
    st.markdown(f'<div class="lm-feasibility">{"".join(cards)}</div>', unsafe_allow_html=True)
    if not preview["order_ok"]:
        st.error(t("ux.check.oversize"))
    if not preview["fleet_ok"]:
        st.error(t("ux.check.overflow"))
    st.markdown(
        f'<p class="lm-packing">{escape(t("ux.check.packing"))}</p>',
        unsafe_allow_html=True,
    )


def preview_stats(payload: dict) -> None:
    scenario = payload["scenario"]
    demands = [customer["demand_totes"] for customer in payload["customers"]]
    preview = capacity_preview(
        demands,
        scenario["vehicle_count"],
        scenario["vehicle_capacity_totes"],
    )
    rows = (
        (t("ux.preview.customers"), str(scenario["customer_count"])),
        (t("ux.preview.demand"), t("ux.preview.demand.value", n=preview["total"])),
        (t("ux.preview.fleet"), t("ux.preview.fleet.value", n=scenario["vehicle_count"])),
        (
            t("ux.preview.capacity"),
            t("ux.preview.capacity.value", n=scenario["vehicle_capacity_totes"]),
        ),
        (t("ux.preview.spare"), t("ux.preview.spare.value", n=preview["spare"])),
    )
    cells = "".join(
        f"<div><dt>{escape(str(label))}</dt><dd>{escape(str(value))}</dd></div>"
        for label, value in rows
    )
    st.markdown(f'<dl class="lm-preview-stats">{cells}</dl>', unsafe_allow_html=True)


def reset_custom_defaults() -> None:
    st.session_state["_custom_config"] = dict(CUSTOM_DEFAULTS)
    st.session_state["_custom_location"] = dict(CUSTOM_LOCATION)
    values = _default_demands(CUSTOM_DEFAULTS["n"])
    st.session_state["_custom_demands"] = values
    st.session_state["_editor_base"] = [
        {"customer": f"C{i + 1:03d}", "totes": value} for i, value in enumerate(values)
    ]
    st.session_state["custom_n"] = CUSTOM_DEFAULTS["n"]
    st.session_state["custom_vans"] = CUSTOM_DEFAULTS["vans"]
    st.session_state["custom_capacity"] = CUSTOM_DEFAULTS["capacity"]
    st.session_state["custom_seed"] = CUSTOM_LOCATION["seed"]
    st.session_state["custom_detour"] = CUSTOM_LOCATION["detour"]
    for key in list(st.session_state.keys()):
        if str(key).startswith("demand_editor_"):
            del st.session_state[key]


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
            status.update(label=t("ux.stage.optimise"))
            search_pulse()
            st.write(t("ux.stage.optimise.detail", n=seconds))
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


def custom_builder() -> tuple[dict | None, bool]:
    st.write(t("ux.custom.help"))
    config = st.session_state.get("_custom_config", dict(CUSTOM_DEFAULTS))
    _heading(t("ux.custom.fleet"))
    left, middle, right = st.columns(3)
    n = int(left.number_input(t("ux.custom.count"), 1, 50, config["n"], key="custom_n"))
    vans = int(middle.number_input(t("ux.custom.vans"), 1, 10, config["vans"], key="custom_vans"))
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
    _heading(t("ux.custom.orders"))
    editor_key = f"demand_editor_{n}"
    if editor_key not in st.session_state:
        previous = st.session_state.get("_custom_demands", [])
        values = previous if len(previous) == n else _default_demands(n)
        st.session_state["_editor_base"] = [
            {"customer": f"C{i + 1:03d}", "totes": value} for i, value in enumerate(values)
        ]
    with st.container(key="demand-editor"):
        rows = st.data_editor(
            st.session_state["_editor_base"],
            key=editor_key,
            disabled=["customer"],
            hide_index=True,
            num_rows="fixed",
            use_container_width=True,
            height=245,
            column_config={
                "customer": st.column_config.TextColumn(t("ux.customer"), width=320),
                "totes": st.column_config.NumberColumn(
                    t("ux.totes"),
                    min_value=1,
                    max_value=100,
                    step=1,
                    width=160,
                    format="%d",
                ),
            },
        )
    demands = [row["totes"] for row in rows]
    st.session_state["_custom_demands"] = demands
    oversized = []
    for row in rows:
        try:
            demand = int(row["totes"])
        except (TypeError, ValueError):
            continue
        if demand > capacity:
            oversized.append((row["customer"], demand))
    if oversized:
        flags = "".join(
            "<p>"
            + escape(
                t("ux.check.oversize.row", id=name, demand=demand, capacity=capacity)
            )
            + "</p>"
            for name, demand in oversized
        )
        st.markdown(f'<div class="lm-order-flags">{flags}</div>', unsafe_allow_html=True)
    preview = capacity_preview(demands, vans, capacity)
    _heading(t("ux.custom.checks"))
    show_capacity(preview, vans, capacity)
    settings = st.session_state.get("_custom_location", dict(CUSTOM_LOCATION))
    with st.expander(t("ux.custom.advanced"), expanded=False):
        seed = int(
            st.number_input(
                t("ux.seed"),
                0,
                2147483647,
                settings["seed"],
                help=t("ux.seed.help"),
                key="custom_seed",
            )
        )
        detour = st.number_input(
            t("ux.detour"),
            1.0,
            2.0,
            settings["detour"],
            step=0.05,
            help=t("ux.detour.help"),
            key="custom_detour",
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
    generate, reset = st.columns([0.62, 0.38], gap="medium")
    generated = None
    with generate:
        if st.button(t("ux.generate"), disabled=not preview["can_generate"], type="primary"):
            generated = call_api(generate_scenario, request, notify=False)
    with reset:
        st.button(t("ux.custom.reset"), type="secondary", on_click=reset_custom_defaults)
    if generated is not None:
        set_scenario(generated["scenario_id"])
        st.session_state["_generated_request"] = request
        st.session_state["_generated_payload"] = call_api(
            get_scenario, generated["scenario_id"], notify=False
        )
    ready = (
        preview["can_generate"]
        and request == st.session_state.get("_generated_request")
        and st.session_state.get("_generated_payload") is not None
    )
    payload = None
    if ready:
        payload = st.session_state["_generated_payload"]
        set_scenario(payload["scenario"]["scenario_id"])
        _banner("ready", t("ux.custom.ready"))
    elif st.session_state.get("_generated_request") is not None:
        _banner("stale", t("ux.custom.stale"), t("ux.custom.changed"))
    return payload, ready


def preset_radio() -> str:
    current = st.session_state.scenario_id
    return st.radio(
        t("ux.presets"),
        PRESETS,
        index=PRESETS.index(current) if current in PRESETS else 0,
        format_func=scenario_label,
        captions=[scenario_caption(preset) for preset in PRESETS],
        key="scenario_presets",
        label_visibility="collapsed",
    )


def load_preset(selected: str) -> tuple[dict | None, bool]:
    set_scenario(selected)
    payload = fetch_preset_scenario(selected)
    return payload, comparison_ready(payload)


page_header(t("ux.scenarios.title"), t("ux.scenarios.subtitle"))
st.markdown('<div class="lm-scenarios-flag"></div>', unsafe_allow_html=True)
if "_custom_open" not in st.session_state:
    st.session_state["_custom_open"] = st.session_state.scenario_id.startswith("GEN_")

custom_open = bool(st.session_state["_custom_open"])
if custom_open:
    st.markdown('<div class="lm-custom-open"></div>', unsafe_allow_html=True)

payload = None
ready = False
widths = [0.56, 0.44] if custom_open else [0.42, 0.58]
inputs, preview_panel = st.columns(widths, gap="medium")
with inputs:
    with st.container(key="scenario-presets-block"):
        _heading(t("ux.presets"))
        selected = preset_radio()
    if custom_open:
        if st.button(t("ux.custom.back"), type="secondary"):
            st.session_state["_custom_open"] = False
            st.rerun()
        _heading(t("ux.custom"))
        payload, ready = custom_builder()
    else:
        st.markdown(
            f'<div class="lm-custom-secondary"><h3>{escape(t("ux.custom"))}</h3>'
            f'<p>{escape(t("ux.custom.intro"))}</p></div>'
            f'<div class="lm-custom-configure-gap"></div>',
            unsafe_allow_html=True,
        )
        with st.container(key="custom-configure"):
            if st.button(t("ux.custom.configure"), type="secondary"):
                st.session_state["_custom_open"] = True
                st.rerun()

with preview_panel:
    with st.container(key="scenario-preview"):
        _heading(t("ux.preview"))
        if not custom_open:
            payload, ready = load_preset(selected)
        if st.session_state.get("_planning_offline"):
            planning_offline_notice()
        if payload is not None:
            st.plotly_chart(customer_map(payload), key="scenario-map", **PLOTLY_CHART_KWARGS)
            preview_stats(payload)
            with st.expander(t("ux.custom.orders")):
                with st.container(key="demand-preview"):
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
                        column_config={
                            t("ux.customer"): st.column_config.TextColumn(
                                t("ux.customer"), width=320
                            ),
                            t("ux.totes"): st.column_config.NumberColumn(
                                t("ux.totes"), width=160, format="%d"
                            ),
                        },
                    )
        elif not st.session_state.get("_planning_offline"):
            empty = t("ux.preview.empty.custom") if custom_open else t("ux.preview.empty")
            st.markdown(
                f'<div class="lm-preview-surface lm-preview-empty">'
                f"<p>{escape(empty)}</p></div>",
                unsafe_allow_html=True,
            )

with st.container(key="scenario-action"):
    search, action = st.columns([0.62, 0.38], gap="medium")
    with search:
        seconds = st.radio(
            t("ux.seconds"),
            [1, 5, 10],
            horizontal=True,
            index=[1, 5, 10].index(st.session_state.solver_time_limit_seconds),
            key="_search_seconds",
            format_func=lambda value: t("ux.seconds.opt", n=value),
            help=t("ux.seconds.help"),
        )
        st.session_state.solver_time_limit_seconds = seconds
    with action:
        if st.button(t("ux.run"), type="primary", disabled=not ready):
            if compare(st.session_state.scenario_id, st.session_state.solver_time_limit_seconds):
                st.switch_page("pages/3_Baseline_vs_Optimised.py")

render_footer()
