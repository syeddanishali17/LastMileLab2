"""Business context, VRP to CVRP, and the Vienna Standard 24 route comparison."""

import streamlit as st

from components import (
    concept_cards,
    cvrp_animation_html,
    page_header,
    render_footer,
    render_overview_about,
)
from i18n import t

st.markdown('<div class="lm-overview-flag"></div>', unsafe_allow_html=True)
page_header(
    t("ux.over.title"),
    t("ux.over.intro"),
    kicker=t("ux.over.kicker"),
    extra=[t("ux.over.feas.hero"), t("ux.over.compare.body")],
    compact=False,
)

st.markdown(
    cvrp_animation_html(t("ux.over.result"), t("ux.over.diagram")),
    unsafe_allow_html=True,
)

if st.button(t("ux.over.cta"), type="primary"):
    st.switch_page("pages/1_Dispatch_Setup.py")

concept_cards(
    [
        (t("ux.over.vrp.title"), t("ux.over.vrp"), t("ux.over.vrp.tip")),
        (t("ux.over.cvrp.title"), t("ux.over.cvrp"), t("ux.over.cvrp.tip")),
        (t("ux.over.feas.title"), t("ux.over.feas"), t("ux.over.feas.tip")),
        (t("ux.over.compare.title"), t("ux.over.compare"), t("ux.over.compare.tip")),
    ]
)

render_overview_about()
render_footer()
