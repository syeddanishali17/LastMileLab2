"""Verify the returned route plan against application checks."""

from __future__ import annotations

from html import escape

import streamlit as st

from components import (
    empty_state,
    expired_result_state,
    fetch_verification_view,
    page_header,
    render_footer,
    static_table,
    status_badge,
)
from display import display_node, format_km, matrix_km_rows
from i18n import t
from inspector import (
    NON_SUCCESS_STATUSES,
    assignment_rows,
    attach_leg_distances,
    check_explanation,
    check_name,
    checks_passed_count,
    cumulative_loads,
    incoming_outgoing,
    outcome_label,
    route_matrix,
    run_metadata_items,
    selected_arcs,
    selected_leg_rows,
    verdict_copy,
)
from state import summary_for_current

page_header(t("nav.inspect"), t("inspect.subtitle"))
st.markdown('<div class="lm-inspect-flag"></div>', unsafe_allow_html=True)

options = []
optimised = summary_for_current("optimised")
baseline = summary_for_current("baseline")
if optimised:
    options.append((t("routes.opt"), optimised["run_id"]))
if baseline:
    options.append((t("routes.base"), baseline["run_id"]))
if not options:
    empty_state(t("inspect.empty.title"), t("inspect.empty.body"))
    render_footer()
    st.stop()

choice = st.radio(
    t("inspect.pick"),
    [item[0] for item in options],
    horizontal=True,
    help=t("inspect.pick.help"),
    key="inspect_plan",
)
run_id = dict(options)[choice]

loaded = fetch_verification_view(run_id, st.session_state.scenario_id)
if loaded.status == "expired":
    expired_result_state()
    render_footer()
    st.stop()
if loaded.status != "ok" or loaded.payload is None:
    st.stop()
run_payload = loaded.payload["run"]
routes_payload = loaded.payload["routes"]
checks_payload = loaded.payload["checks"]
scenario_payload = loaded.payload["scenario"]
checks = list(checks_payload.get("checks") or [])
status = str(run_payload.get("status") or "")

if status in NON_SUCCESS_STATUSES:
    status_badge(status, run_type=run_payload.get("run_type"))

passed, total = checks_passed_count(checks)
ok, verdict = verdict_copy(checks)
kind = "is-pass" if ok else "is-fail"
icon = "✓" if ok else "!"
st.markdown(
    f'<div class="lm-inspect-verdict {kind}" role="status">'
    f'<span class="lm-inspect-verdict-icon" aria-hidden="true">{icon}</span>'
    f'<span class="lm-inspect-verdict-text">{escape(verdict)}</span>'
    "</div>",
    unsafe_allow_html=True,
)
st.markdown(
    (
        f'<p class="lm-inspect-count">'
        f'{escape(t("inspect.verdict.count", passed=passed, total=total))}</p>'
    ),
    unsafe_allow_html=True,
)

st.markdown(
    f'<p class="lm-inspect-label">{escape(t("inspect.checks"))}</p>',
    unsafe_allow_html=True,
)
check_rows = []
for check in checks:
    result = outcome_label(bool(check.get("passed")))
    result_kind = "is-pass" if check.get("passed") else "is-fail"
    check_rows.append(
        "<tr>"
        f"<th scope='row'>{escape(check_name(check))}</th>"
        f"<td class='lm-inspect-result {result_kind}'>{escape(result)}</td>"
        f"<td>{escape(check_explanation(check))}</td>"
        "</tr>"
    )
st.markdown(
    '<div class="lm-inspect-table-wrap" tabindex="0">'
    '<table class="lm-inspect-checks">'
    "<thead><tr>"
    f"<th scope='col'>{escape(t('inspect.col.check'))}</th>"
    f"<th scope='col'>{escape(t('inspect.col.result'))}</th>"
    f"<th scope='col'>{escape(t('inspect.col.explain'))}</th>"
    "</tr></thead>"
    f"<tbody>{''.join(check_rows)}</tbody></table></div>",
    unsafe_allow_html=True,
)

st.markdown(
    f'<p class="lm-inspect-label">{escape(t("inspect.meta"))}</p>',
    unsafe_allow_html=True,
)
meta_items = "".join(
    "<div class='lm-inspect-meta-row'>"
    f"<dt>{escape(label)}</dt>"
    f"<dd class='{escape(css)}'>{escape(value)}</dd>"
    "</div>"
    for label, value, css in run_metadata_items(run_payload)
)
st.markdown(
    f"<dl class='lm-inspect-meta'>{meta_items}</dl>",
    unsafe_allow_html=True,
)
st.markdown(
    f'<p class="lm-inspect-scope">{escape(t("inspect.scope"))}</p>',
    unsafe_allow_html=True,
)

arcs = attach_leg_distances(
    selected_arcs(routes_payload.get("vehicle_kpis", [])),
    routes_payload.get("stops", []),
)
node_ids = scenario_payload["distance_matrix"]["node_ids"]

with st.expander(t("inspect.view.assignments"), expanded=False):
    st.caption(t("inspect.demand.cap"))
    static_table(
        assignment_rows(checks_payload.get("assignments", [])),
        numeric_columns={
            t("inspect.col.required"),
            t("inspect.col.delivered"),
            t("inspect.col.visits"),
        },
        row_header=t("inspect.col.customer"),
    )

with st.expander(t("inspect.view.legs"), expanded=False):
    st.caption(t("inspect.arcs.cap"))
    static_table(
        incoming_outgoing(arcs, node_ids),
        numeric_columns={t("inspect.col.outgoing"), t("inspect.col.incoming")},
        row_header=t("inspect.cum.node"),
    )
    static_table(
        selected_leg_rows(arcs),
        numeric_columns={t("inspect.col.selected")},
        row_header=t("table.vehicle"),
    )
    st.caption(t("inspect.matrix.all"))
    for vehicle in routes_payload.get("vehicle_kpis", []):
        if not vehicle.get("is_used"):
            continue
        st.markdown(t("inspect.matrix.van", id=vehicle["vehicle_id"]))
        st.dataframe(
            route_matrix(node_ids, vehicle.get("sequence") or []),
            use_container_width=True,
            hide_index=True,
        )

with st.expander(t("inspect.view.loads"), expanded=False):
    st.caption(t("inspect.loads.cap"))
    static_table(
        cumulative_loads(routes_payload.get("stops", [])),
        numeric_columns={
            t("inspect.cum.sequence"),
            t("inspect.cum.demand"),
            t("inspect.cum.served"),
        },
        row_header=t("table.vehicle"),
    )

with st.expander(t("inspect.view.distance"), expanded=False):
    st.caption(t("inspect.obj", km=format_km(run_payload.get("objective_distance_metres"))))
    depot_id = scenario_payload["depot"]["depot_id"]
    st.caption(t("inspect.depot", id=depot_id, label=display_node(depot_id)))
    static_table(
        selected_leg_rows(arcs),
        numeric_columns={t("inspect.col.selected")},
        row_header=t("table.vehicle"),
    )

with st.expander(t("inspect.view.matrix"), expanded=False):
    st.caption(t("inspect.dist.cap"))
    st.dataframe(
        matrix_km_rows(scenario_payload["distance_matrix"]),
        use_container_width=True,
        hide_index=True,
    )

st.page_link("pages/3_Baseline_vs_Optimised.py", label=t("nav.compare"))
render_footer()
