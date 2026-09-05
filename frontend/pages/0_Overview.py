"""Business context, VRP to CVRP, and a clearly labelled published example."""

import streamlit as st

from components import (
    concept_cards,
    cvrp_animation_html,
    gloss_first_tote,
    kpi_cards,
    page_header,
    render_footer,
    section,
    term,
)
from display import format_improvement, format_km
from i18n import t

page_header(
    t("ux.over.title"),
    t("ux.over.intro"),
    kicker=t("ux.over.kicker"),
    extra=t("ux.over.compare.body"),
    context=t("ux.over.context"),
    compact=False,
)

concept_cards(
    [
        (t("ux.over.vrp.title"), t("ux.over.vrp")),
        (
            t("ux.over.cvrp.title"),
            gloss_first_tote(
                t("ux.over.cvrp").replace(
                    "Capacitated Vehicle Routing Problem (CVRP)",
                    term("Capacitated Vehicle Routing Problem (CVRP)", "tip.cvrp"),
                    1,
                )
            ),
        ),
        (t("ux.over.feas.title"), t("ux.over.feas")),
        (t("ux.over.compare.title"), t("ux.over.compare")),
    ]
)

st.markdown(
    cvrp_animation_html(t("ux.over.result"), t("ux.over.diagram")),
    unsafe_allow_html=True,
)

section(t("ux.over.proof"))
kpi_cards(
    [
        (t("ux.proof.served"), "24 / 24"),
        (t("ux.kpi.baseline"), format_km(122394)),
        (t("ux.kpi.optimised"), format_km(97193)),
        (t("ux.kpi.saving"), format_improvement(20.6)),
    ]
)
st.caption(t("ux.over.proof.cap"))
st.caption(t("ux.over.future"))
st.caption(t("ux.over.disclosure"))

if st.button(t("ux.over.cta"), type="primary"):
    st.switch_page("pages/1_Dispatch_Setup.py")
st.page_link("pages/6_Methodology.py", label=t("nav.method"))
render_footer()
