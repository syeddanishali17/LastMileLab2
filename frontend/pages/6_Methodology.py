"""Vehicle routing model, constraints, baseline and OR-Tools search."""

import streamlit as st

from components import (
    constraint_cards,
    gloss_first_tote,
    html_write,
    methodology_animation_html,
    page_header,
    render_footer,
    section,
    with_terms,
)
from i18n import t

page_header(t("ux.method.title"), t("ux.method.subtitle"))
st.markdown('<div class="lm-method-flag"></div>', unsafe_allow_html=True)

section(t("ux.method.vrp.title"))
html_write(
    with_terms(
        t("ux.method.vrp"),
        [("Vehicle Routing Problem (VRP)", "tip.vrp")],
    )
)
st.write(t("ux.method.vrp.feas"))

section(t("ux.method.cvrp.title"))
html_write(
    gloss_first_tote(
        with_terms(
            t("ux.method.cvrp"),
            [("Capacitated Vehicle Routing Problem (CVRP)", "tip.cvrp")],
        )
    )
)
st.write(t("ux.method.cvrp.unused"))

section(t("ux.method.obj.title"))
st.write(t("ux.method.obj"))
with st.expander(t("ux.method.obj.formula.title")):
    st.code(t("ux.method.obj.formula"))
    st.caption(t("ux.method.obj.formula.note"))

section(t("ux.method.cons.title"))
constraint_cards(
    [
        (t("ux.method.cons.service.title"), t("ux.method.cons.service")),
        (t("ux.method.cons.capacity.title"), t("ux.method.cons.capacity")),
        (t("ux.method.cons.unsplit.title"), t("ux.method.cons.unsplit")),
        (t("ux.method.cons.depot.title"), t("ux.method.cons.depot")),
        (t("ux.method.cons.route.title"), t("ux.method.cons.route")),
    ]
)

st.markdown(methodology_animation_html(), unsafe_allow_html=True)

section(t("ux.method.baseline.title"))
html_write(
    with_terms(
        t("ux.method.baseline"),
        [
            ("nearest-neighbour", "tip.nn"),
            ("Nächster-Nachbar", "tip.nn"),
        ],
    )
)
st.write(t("ux.method.baseline.limit"))

section(t("ux.method.opensolver.title"))
st.write(t("ux.method.opensolver"))

section(t("ux.method.solver.title"))
st.write(t("ux.method.solver"))
html_write(
    with_terms(
        t("ux.method.solver.limit"),
        [
            ("search limit", "tip.search"),
            ("Suchlimit", "tip.search"),
            ("feasible solution", "tip.feasible"),
            ("zulässige Lösung", "tip.feasible"),
        ],
    )
)
st.write(t("ux.method.solver.none"))

section(t("ux.method.impl.title"))
st.write(t("ux.method.impl"))

section(t("ux.method.assumptions.title"))
html_write(
    with_terms(
        t("ux.method.assumptions"),
        [
            ("Haversine", "tip.haversine"),
            ("detour factor", "tip.detour"),
            ("Umwegfaktor", "tip.detour"),
        ],
    )
)
st.caption(t("ux.method.scope.note"))

section(t("ux.plan.audit"))
st.write(t("ux.method.audit"))
st.page_link("pages/4_Model_Inspector.py", label=t("nav.inspect"))
render_footer()
