"""Route comparison, with optional baseline and optimized detail views."""

from html import escape

import streamlit as st

from components import (
    empty_state,
    expired_result_state,
    export_buttons,
    heading_with_tip,
    kpi_cards,
    page_header,
    render_footer,
    resolve_plan_bundle,
    section,
    static_table,
    status_badge,
)
from display import (
    VEHICLE_COLOURS,
    display_node,
    format_improvement,
    format_km,
    format_sequence,
    plan_comparison_summary,
    plans_comparable,
    scenario_label,
)
from i18n import t
from maps import PLOTLY_PLAN_CHART_KWARGS, route_map
from state import summary_for_current

PLAN_VIEWS = ("comparison", "baseline", "optimised")
ROUTE_LEGEND_VEHICLES = ("V01", "V02", "V03", "V04")


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


def panel_distance(run: dict) -> str:
    if run["comparison_eligible"]:
        return format_km(run["objective_distance_metres"])
    if run.get("partial_distance_metres") is not None:
        return t("ux.plan.partial", km=format_km(run["partial_distance_metres"]))
    return t("common.na")


def check_outcome_label(passed: bool) -> str:
    return t("ux.plan.check.passed") if passed else t("ux.plan.check.failed")


def render_feasible_status(run: dict) -> None:
    if run.get("status") == "feasible":
        st.markdown(
            f'<p class="lm-plan-status">{escape(t("ux.plan.feasible"))}</p>'
            f'<p class="lm-plan-status-text">{escape(t("ux.plan.feasible.text"))}</p>',
            unsafe_allow_html=True,
        )
        return
    status_badge(run.get("status"), run_type=run.get("run_type"))


def render_plan_verdict(lead: str, detail: str | None, comparable: bool) -> None:
    cue = t("ux.plan.result.cue") if comparable else t("ux.plan.ineligible.cue")
    st.markdown(
        f'<p class="lm-plan-verdict-cue">{escape(cue)}</p>',
        unsafe_allow_html=True,
    )
    if comparable:
        st.markdown(
            f'<p class="lm-plan-verdict">{escape(lead)}</p>',
            unsafe_allow_html=True,
        )
        return
    st.info(lead)
    if detail:
        for line in detail.splitlines():
            st.write(line)


def render_route_legend() -> None:
    items = []
    for index, label in enumerate(ROUTE_LEGEND_VEHICLES):
        colour = VEHICLE_COLOURS[index]
        items.append(
            f'<span class="lm-plan-legend-item" role="listitem">'
            f'<span class="lm-plan-legend-swatch" style="background:{colour}" '
            f'aria-hidden="true"></span>{escape(label)}</span>'
        )
    st.markdown(
        '<div class="lm-plan-legend">'
        f'<div class="lm-plan-legend-swatches" role="list">{"".join(items)}</div>'
        f'<p class="lm-plan-legend-note">{escape(t("ux.plan.map.numbers"))}</p>'
        "</div>",
        unsafe_allow_html=True,
    )


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


def route_sequence_blocks(routes: dict) -> str:
    blocks = []
    for vehicle in routes["vehicle_kpis"]:
        sequence = format_sequence(vehicle.get("sequence") or [])
        blocks.append(
            f"<p class='lm-plan-seq'><strong>{escape(vehicle['vehicle_id'])}</strong><br/>"
            f"{escape(sequence)}</p>"
        )
    return "".join(blocks)


def route_sequences(routes: dict, *, as_expander: bool = True) -> None:
    markup = route_sequence_blocks(routes)
    if as_expander:
        with st.expander(t("ux.plan.sequences")):
            st.markdown(markup, unsafe_allow_html=True)
        return
    st.caption(t("ux.plan.sequences"))
    st.markdown(markup, unsafe_allow_html=True)


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


def check_result_cell(passed: bool) -> str:
    kind = "is-pass" if passed else "is-fail"
    return f'<td class="lm-plan-check {kind}">{escape(check_outcome_label(passed))}</td>'


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
            f"{check_result_cell(bool(check.get('passed')))}"
            f"{check_result_cell(bool(other.get('passed')))}"
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
        + escape(
            f"{check_outcome_label(bool(check.get('passed')))} · "
            f"{t('check.audit.' + str(check.get('code')))}"
        )
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


def render_plan_side(*, kind: str, run: dict, figure, map_key: str) -> None:
    if kind == "baseline":
        heading_with_tip(
            t("ux.baseline"),
            t("ux.plan.baseline.method.tip"),
            level="h3",
        )
    else:
        heading_with_tip(t("ux.optimised.short"), t("ux.plan.opt.tip"), level="h3")
    if run.get("status") != "feasible":
        status_badge(run.get("status"), run_type=run.get("run_type"))
    if run.get("unserved_customer_ids"):
        st.warning(t("ux.plan.unserved", ids=", ".join(run["unserved_customer_ids"])))
    st.markdown(
        f'<p class="lm-plan-distance">{escape(panel_distance(run))}</p>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(figure, key=map_key, **PLOTLY_PLAN_CHART_KWARGS)


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
    lead, detail = plan_comparison_summary(baseline, optimised)
    render_plan_verdict(lead, detail, comparable)
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
    with st.container(key="plan-pair"):
        render_route_legend()
        left, right = st.columns(2, gap="large")
        with left:
            render_plan_side(
                kind="baseline",
                run=baseline,
                figure=figures["baseline"],
                map_key="map-baseline",
            )
        with right:
            render_plan_side(
                kind="optimised",
                run=optimised,
                figure=figures["optimised"],
                map_key="map-optimised",
            )
    with st.container(key="plan-route-details"):
        section(t("ux.plan.routes"))
        with st.expander(t("ux.plan.view.baseline"), expanded=False):
            vehicle_summary(bundle["baseline"]["routes"])
            route_sequences(bundle["baseline"]["routes"], as_expander=False)
        with st.expander(t("ux.plan.view.optimised"), expanded=False):
            vehicle_summary(bundle["optimised"]["routes"])
            route_sequences(bundle["optimised"]["routes"], as_expander=False)
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
    render_route_legend()
    st.plotly_chart(figures[kind], key=f"map-{kind}-detail", **PLOTLY_PLAN_CHART_KWARGS)
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

loaded = resolve_plan_bundle(baseline, optimised, st.session_state.scenario_id)
if loaded.status == "expired":
    expired_result_state()
    render_footer()
    st.stop()
if loaded.status != "ok" or loaded.payload is None:
    st.stop()
bundle = loaded.payload

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
