"""Route comparison, with optional baseline and optimized detail views."""

from html import escape

import streamlit as st

from api_client import get_checks, get_routes, get_run, get_scenario
from components import (
    call_api,
    empty_state,
    export_buttons,
    heading_with_tip,
    kpi_cards,
    page_header,
    render_footer,
    section,
    static_table,
    status_badge,
    with_terms,
)
from display import (
    display_node,
    format_improvement,
    format_km,
    format_sequence,
    plan_comparison_summary,
    plans_comparable,
    scenario_label,
)
from i18n import t
from maps import PLOTLY_CHART_KWARGS, route_map
from state import summary_for_current

PLAN_VIEWS = ("comparison", "baseline", "optimised")


def _tab_label(code: str) -> str:
    return {
        "comparison": t("ux.plan.tab.comparison"),
        "baseline": t("ux.plan.tab.baseline"),
        "optimised": t("ux.plan.tab.optimised"),
    }[code]


def total_distance_label(run: dict) -> str:
    if run["comparison_eligible"]:
        return t("ux.plan.total", km=format_km(run["objective_distance_metres"]))
    if run.get("partial_distance_metres") is not None:
        return t("ux.plan.partial", km=format_km(run["partial_distance_metres"]))
    return t("ux.plan.total", km=t("common.na"))


def km_or_na(run: dict) -> str:
    if run["comparison_eligible"]:
        return format_km(run["objective_distance_metres"])
    return t("common.na")


def render_feasible_status(run: dict) -> None:
    if run.get("status") == "feasible":
        st.markdown(
            f'<p class="lm-plan-status">{escape(t("ux.plan.feasible"))}</p>'
            f'<p class="lm-plan-status-text">{escape(t("ux.plan.feasible.text"))}</p>',
            unsafe_allow_html=True,
        )
        return
    status_badge(run.get("status"), run_type=run.get("run_type"))


def vehicle_summary(routes: dict) -> None:
    static_table(
        [
            {
                t("ux.van"): vehicle["vehicle_id"],
                t("ux.plan.load"): (
                    f"{vehicle['assigned_demand_totes']} / {vehicle['capacity_totes']} "
                    f"{t('ux.plan.totes')}"
                ),
                t("ux.plan.customers"): vehicle["customer_count"],
                t("ux.plan.travelled"): format_km(vehicle["route_distance_metres"]),
            }
            for vehicle in routes["vehicle_kpis"]
        ],
        row_header=t("ux.van"),
        numeric_columns={
            t("ux.plan.load"),
            t("ux.plan.customers"),
            t("ux.plan.travelled"),
        },
    )


def route_sequences(routes: dict) -> None:
    with st.expander(t("ux.plan.sequences")):
        blocks = []
        for vehicle in routes["vehicle_kpis"]:
            sequence = format_sequence(vehicle.get("sequence") or [])
            blocks.append(
                f"<p class='lm-plan-seq'><strong>{escape(vehicle['vehicle_id'])}</strong><br/>"
                f"{escape(sequence)}</p>"
            )
        st.markdown("".join(blocks), unsafe_allow_html=True)


def detailed_route_data(routes: dict) -> None:
    with st.expander(t("ux.plan.details")):
        st.caption(t("ux.plan.details.cap"))
        static_table(
            [
                {
                    t("ux.van"): stop["vehicle_id"],
                    t("ux.plan.col.stop"): stop["sequence_number"],
                    t("ux.plan.col.location"): display_node(stop["node_id"]),
                    t("ux.plan.col.demand"): stop["demand_totes"],
                    t("ux.plan.col.leg"): format_km(stop["leg_distance_metres"]),
                    t("ux.plan.col.cumulative"): stop["load_after_service_totes"],
                }
                for stop in routes["stops"]
            ],
            numeric_columns={
                t("ux.plan.col.stop"),
                t("ux.plan.col.demand"),
                t("ux.plan.col.leg"),
                t("ux.plan.col.cumulative"),
            },
        )


def checks_by_code(checks: list[dict]) -> dict[str, dict]:
    return {str(check.get("code")): check for check in checks}


def all_checks_passed(checks: list[dict]) -> bool:
    return bool(checks) and all(check.get("passed") for check in checks)


def validation_matrix(bundle: dict) -> None:
    baseline_checks = bundle["baseline"]["checks"]["checks"]
    optimised_checks = checks_by_code(bundle["optimised"]["checks"]["checks"])
    rows = []
    for check in baseline_checks:
        code = str(check.get("code"))
        other = optimised_checks.get(code, {})
        rows.append(
            "<tr>"
            f"<th scope='row'>{escape(t(f'check.audit.{code}'))}</th>"
            f"<td>{'✓' if check.get('passed') else '✗'}</td>"
            f"<td>{'✓' if other.get('passed') else '✗'}</td>"
            "</tr>"
        )
    st.markdown(
        '<table class="lm-plan-matrix">'
        "<thead><tr>"
        f"<th scope='col'>{escape(t('ux.plan.validation.check'))}</th>"
        f"<th scope='col'>{escape(t('ux.plan.baseline.heading'))}</th>"
        f"<th scope='col'>{escape(t('ux.plan.opt.heading'))}</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>",
        unsafe_allow_html=True,
    )
    if all_checks_passed(baseline_checks) and all_checks_passed(
        bundle["optimised"]["checks"]["checks"]
    ):
        st.caption(t("ux.plan.validation.intro"))
    else:
        st.warning(t("ux.plan.audit.failed"))


def validation_list(checks: list[dict]) -> None:
    items = "".join(
        "<li>"
        + escape(("✓ " if check.get("passed") else "✗ ") + t(f"check.audit.{check.get('code')}"))
        + "</li>"
        for check in checks
    )
    st.markdown(f'<ul class="lm-plan-checks">{items}</ul>', unsafe_allow_html=True)
    if not all_checks_passed(checks):
        st.warning(t("ux.plan.audit.failed"))


def render_exports(bundle: dict) -> None:
    with st.container(key="plan-exports"):
        section(t("ux.plan.exports"), t("ux.plan.exports.cap"))
        left, right = st.columns(2)
        with left:
            st.markdown(f"**{t('ux.plan.export.baseline')}**")
            export_buttons(bundle["baseline"]["run"]["run_id"], visible=True)
        with right:
            st.markdown(f"**{t('ux.plan.export.optimised')}**")
            export_buttons(bundle["optimised"]["run"]["run_id"], visible=True)


def render_technical_review() -> None:
    with st.container(key="plan-review"):
        section(t("ux.plan.review"), t("ux.plan.review.body"))
        left, right = st.columns(2)
        with left:
            if st.button(t("nav.inspect"), type="secondary", key="plan-review-inspect"):
                st.switch_page("pages/4_Model_Inspector.py")
        with right:
            if st.button(t("nav.method"), type="secondary", key="plan-review-method"):
                st.switch_page("pages/6_Methodology.py")


def render_plan_side(
    *,
    kind: str,
    run: dict,
    routes: dict,
    figure,
    comparable: bool,
    reduction: str,
    map_key: str,
) -> None:
    if kind == "baseline":
        heading_with_tip(
            t("ux.plan.baseline.heading"),
            t("ux.plan.baseline.method.tip"),
            level="h3",
        )
        st.caption(t("ux.plan.baseline.method"))
    else:
        heading_with_tip(t("ux.plan.opt.heading"), t("ux.plan.opt.tip"), level="h3")
    render_feasible_status(run)
    if run.get("unserved_customer_ids"):
        st.warning(t("ux.plan.unserved", ids=", ".join(run["unserved_customer_ids"])))
    st.markdown(f"**{total_distance_label(run)}**")
    if kind == "optimised" and comparable:
        st.caption(t("ux.plan.reduction", reduction=reduction))
    st.plotly_chart(figure, key=map_key, **PLOTLY_CHART_KWARGS)
    vehicle_summary(routes)
    route_sequences(routes)


def render_comparison(bundle: dict, figures: dict, comparable: bool) -> None:
    baseline = bundle["baseline"]["run"]
    optimised = bundle["optimised"]["run"]
    reduction = (
        format_improvement(optimised["distance_improvement_percentage"])
        if comparable
        else t("common.na")
    )
    heading_with_tip(t("ux.plan.why.title"), t("ux.plan.why.tip"))
    st.write(t("ux.plan.why.body"))
    section(t("ux.plan.summary"))
    lead, detail = plan_comparison_summary(baseline, optimised)
    if comparable:
        st.write(lead)
    else:
        st.info(lead)
        if detail:
            for line in detail.splitlines():
                st.write(line)
    kpi_cards(
        [
            (t("ux.plan.kpi.baseline"), km_or_na(baseline)),
            (t("ux.plan.kpi.optimised"), km_or_na(optimised)),
            (t("ux.plan.kpi.saving"), reduction),
            (
                t("ux.plan.kpi.served"),
                f"{optimised['customers_served']} / {optimised['customers_total']}",
            ),
        ]
    )
    st.caption(t("ux.plan.map.guide"))
    st.markdown(
        with_terms(t("ux.plan.map.numbers"), [("Depot", "ux.plan.map.depot")]),
        unsafe_allow_html=True,
    )
    with st.container(key="plan-pair"):
        left, right = st.columns(2, gap="large")
        with left:
            render_plan_side(
                kind="baseline",
                run=baseline,
                routes=bundle["baseline"]["routes"],
                figure=figures["baseline"],
                comparable=comparable,
                reduction=reduction,
                map_key="map-baseline",
            )
        with right:
            render_plan_side(
                kind="optimised",
                run=optimised,
                routes=bundle["optimised"]["routes"],
                figure=figures["optimised"],
                comparable=comparable,
                reduction=reduction,
                map_key="map-optimised",
            )
    section(t("ux.plan.validation"))
    validation_matrix(bundle)
    if st.button(t("ux.plan.validation.open"), type="secondary", key="plan-inspect"):
        st.switch_page("pages/4_Model_Inspector.py")
    render_exports(bundle)
    render_technical_review()


def render_detail(bundle: dict, figures: dict, kind: str, comparable: bool) -> None:
    run = bundle[kind]["run"]
    routes = bundle[kind]["routes"]
    reduction = (
        format_improvement(bundle["optimised"]["run"]["distance_improvement_percentage"])
        if comparable
        else t("common.na")
    )
    if kind == "baseline":
        section(t("ux.plan.baseline.heading"), t("ux.plan.baseline.sub"))
        st.caption(t("ux.plan.baseline.method"))
    else:
        heading_with_tip(t("ux.plan.opt.heading"), t("ux.plan.opt.tip"))
        st.caption(t("ux.plan.opt.sub"))
    render_feasible_status(run)
    if run.get("unserved_customer_ids"):
        st.warning(t("ux.plan.unserved", ids=", ".join(run["unserved_customer_ids"])))
    st.markdown(f"**{total_distance_label(run)}**")
    if kind == "optimised" and comparable:
        st.caption(t("ux.plan.reduction", reduction=reduction))
    st.caption(t("ux.plan.map.guide"))
    st.markdown(
        with_terms(t("ux.plan.map.numbers"), [("Depot", "ux.plan.map.depot")]),
        unsafe_allow_html=True,
    )
    st.plotly_chart(figures[kind], key=f"map-{kind}-detail", **PLOTLY_CHART_KWARGS)
    vehicle_summary(routes)
    route_sequences(routes)
    detailed_route_data(routes)
    section(t("ux.plan.validation"))
    validation_list(bundle[kind]["checks"]["checks"])
    if st.button(t("ux.plan.validation.open"), type="secondary", key=f"plan-inspect-{kind}"):
        st.switch_page("pages/4_Model_Inspector.py")


page_header(t("ux.plan.title"), t("ux.plan.subtitle"))
st.markdown('<div class="lm-plan-flag"></div>', unsafe_allow_html=True)
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
    st.session_state.plan_view = "comparison"

baseline = bundle["baseline"]["run"]
optimised = bundle["optimised"]["run"]
if baseline["scenario_id"] != optimised["scenario_id"]:
    st.error(t("compare.mismatch"))
    st.stop()

st.caption(t("ux.plan.scenario", name=scenario_label(st.session_state.scenario_id)))
if st.session_state.get("plan_view") not in PLAN_VIEWS:
    st.session_state.plan_view = "comparison"
view = st.segmented_control(
    t("ux.plan.pick"),
    options=list(PLAN_VIEWS),
    format_func=_tab_label,
    key="plan_view",
    label_visibility="collapsed",
)
if view not in PLAN_VIEWS:
    view = "comparison"

comparable = plans_comparable(baseline, optimised)
figures = {
    kind: route_map(
        bundle["scenario"],
        bundle[kind]["routes"],
        unserved_ids=bundle[kind]["run"]["unserved_customer_ids"],
    )
    for kind in ("baseline", "optimised")
}

if view == "comparison":
    render_comparison(bundle, figures, comparable)
elif view == "baseline":
    render_detail(bundle, figures, "baseline", comparable)
else:
    render_detail(bundle, figures, "optimised", comparable)
render_footer()
