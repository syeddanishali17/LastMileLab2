"""Vehicle routing model, constraints, baseline and OR-Tools search."""

import streamlit as st

from components import (
    constraint_cards,
    gloss_first_tote,
    html_write,
    methodology_animation_html,
    page_header,
    reading_cards_html,
    render_footer,
    section,
    toc_html,
    with_terms,
)
from i18n import t

FURTHER_READING = (
    (
        "Computers & Operations Research (2019)",
        "Visual attractiveness in routing problems: a review",
        "ux.method.reading.visual",
        "https://ri.conicet.gov.ar/handle/11336/103527",
    ),
    (
        "arXiv · Amazon routing challenge (2022)",
        "Learning from drivers to tackle the Amazon Last Mile Routing Research Challenge",
        "ux.method.reading.drivers",
        "https://arxiv.org/abs/2205.04001",
    ),
    (
        "DSpace@MIT · Networks (2019)",
        "An empirical validation and data-driven extension of continuum approximation "
        "approaches for urban route distances",
        "ux.method.reading.circuity",
        "https://dspace.mit.edu/handle/1721.1/140763",
    ),
    (
        "DSpace@MIT · PhD thesis (2018)",
        "Effects of road-network circuity on strategic decisions in urban logistics",
        "ux.method.reading.thesis",
        "https://dspace.mit.edu/handle/1721.1/119911",
    ),
    (
        "MIT CTL · Transportation Science",
        "2021 Amazon Last Mile Routing Research Challenge: Data Set",
        "ux.method.reading.amazon",
        "https://ctl.mit.edu/publications/2021-amazon-last-mile-routing-research-challenge-data-set",
    ),
    (
        "DSpace@MIT",
        "Technical Proceedings of the Amazon Last Mile Routing Research Challenge",
        "ux.method.reading.proceedings",
        "https://dspace.mit.edu/handle/1721.1/131235",
    ),
    (
        "Google OR-Tools",
        "Vehicle Routing Problem guide",
        "ux.method.reading.ortools",
        "https://developers.google.com/optimization/routing",
    ),
    (
        "Google Research",
        "OR-Tools' Vehicle Routing Solver: a generic constraint-programming solver "
        "with heuristic search",
        "ux.method.reading.gls",
        "https://research.google/pubs/pub52024/",
    ),
)

page_header(t("ux.method.title"), t("ux.method.subtitle"))
st.markdown('<div class="lm-method-flag"></div>', unsafe_allow_html=True)
st.markdown(
    toc_html(
        [
            ("vrp", t("ux.method.vrp.title")),
            ("constraints", t("ux.method.cons.title")),
            ("baseline", t("ux.method.baseline.title")),
            ("solver", t("ux.method.solver.title")),
            ("continuum", t("ux.method.ca.title")),
            ("attractiveness", t("ux.method.quality.title")),
            ("scope", t("ux.method.assumptions.title")),
            ("reading", t("ux.method.reading.title")),
        ],
        t("ux.method.toc"),
    ),
    unsafe_allow_html=True,
)

section(t("ux.method.vrp.title"), anchor="vrp")
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
    # Plain text: Python highlighting would colour "and"/"of" in the formula as keywords.
    st.code(t("ux.method.obj.formula"), language=None)
    st.caption(t("ux.method.obj.formula.note"))

section(t("ux.method.cons.title"), anchor="constraints")
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

section(t("ux.method.baseline.title"), anchor="baseline")
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

section(t("ux.method.solver.title"), anchor="solver")
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

section(t("ux.method.ca.title"), anchor="continuum")
st.write(t("ux.method.ca"))
st.code(t("ux.method.ca.formula"), language=None)
st.caption(t("ux.method.ca.note"))

section(t("ux.method.quality.title"), anchor="attractiveness")
st.write(t("ux.method.quality"))

section(t("ux.method.opensolver.title"))
st.write(t("ux.method.opensolver"))

section(t("ux.method.impl.title"))
st.write(t("ux.method.impl"))

section(t("ux.method.assumptions.title"), anchor="scope")
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
with st.container(key="method-inspect"):
    if st.button(t("ux.method.inspect"), type="secondary"):
        st.switch_page("pages/4_Model_Inspector.py")

section(t("ux.method.reading.title"), t("ux.method.reading.cap"), anchor="reading")
st.markdown(
    reading_cards_html(
        [(source, title, t(why_key), url) for source, title, why_key, url in FURTHER_READING]
    ),
    unsafe_allow_html=True,
)
render_footer()
