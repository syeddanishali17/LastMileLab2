"""Business context, VRP to CVRP, and the Vienna Standard 24 route comparison."""

from html import escape

import streamlit as st

from components import (
    concept_cards,
    cvrp_animation_html,
    kpi_cards,
    page_header,
    render_footer,
)
from display import format_improvement, format_km
from i18n import t

st.markdown('<div class="lm-overview-flag"></div>', unsafe_allow_html=True)
page_header(
    t("ux.over.title"),
    t("ux.over.intro"),
    kicker=t("ux.over.kicker"),
    extra=[t("ux.over.feas.hero"), t("ux.over.compare.body")],
    author=t("ux.over.author"),
    compact=False,
)

concept_cards(
    [
        (t("ux.over.vrp.title"), t("ux.over.vrp"), t("ux.over.vrp.tip")),
        (t("ux.over.cvrp.title"), t("ux.over.cvrp"), t("ux.over.cvrp.tip")),
        (t("ux.over.feas.title"), t("ux.over.feas"), t("ux.over.feas.tip")),
        (t("ux.over.compare.title"), t("ux.over.compare"), t("ux.over.compare.tip")),
    ]
)

st.markdown(
    cvrp_animation_html(t("ux.over.result"), t("ux.over.diagram")),
    unsafe_allow_html=True,
)

st.markdown(
    f'<p class="lm-proof-kicker">{escape(t("ux.over.proof.kicker"))}</p>',
    unsafe_allow_html=True,
)
kpi_cards(
    [
        (t("ux.proof.served"), "24 / 24"),
        (t("ux.kpi.baseline"), format_km(122394)),
        (t("ux.kpi.optimised"), format_km(97193)),
        (t("ux.kpi.saving"), format_improvement(20.6)),
    ]
)
st.caption(t("ux.over.proof.tech"))

if st.button(t("ux.over.cta"), type="primary"):
    st.switch_page("pages/1_Dispatch_Setup.py")

render_footer()
