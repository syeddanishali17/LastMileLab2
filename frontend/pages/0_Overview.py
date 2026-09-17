"""Business context, VRP to CVRP, and the routing-model explainer."""

import streamlit as st

from components import (
    concept_cards,
    page_header,
    render_cvrp_animation,
    render_footer,
    render_overview_about,
)
from i18n import t

st.markdown('<div class="lm-overview-flag"></div>', unsafe_allow_html=True)
page_header(
    t("ux.over.title"),
    t("ux.over.intro"),
    kicker=t("ux.over.kicker"),
    compact=False,
)

render_cvrp_animation()

if st.button(t("ux.over.cta"), type="primary", key="overview-cta"):
    st.switch_page("pages/1_Dispatch_Setup.py")

concept_cards(
    [
        (
            t("ux.over.vrp.label"),
            t("ux.over.vrp.title"),
            t("ux.over.vrp"),
            t("ux.over.vrp.tip"),
        ),
        (
            t("ux.over.cvrp.label"),
            t("ux.over.cvrp.title"),
            t("ux.over.cvrp"),
            t("ux.over.cvrp.tip"),
        ),
        (
            t("ux.over.feas.label"),
            t("ux.over.feas.title"),
            t("ux.over.feas"),
            t("ux.over.feas.tip"),
        ),
        (
            t("ux.over.compare.label"),
            t("ux.over.compare.title"),
            t("ux.over.compare"),
            t("ux.over.compare.tip"),
        ),
    ],
    kicker=t("ux.over.model.kicker"),
)

render_overview_about()
render_footer()
