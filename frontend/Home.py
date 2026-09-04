"""LastMile Lab: ViennaCart CVRP Dispatch Planner."""

from __future__ import annotations

import streamlit as st

from api_client import backend_url, get_health
from components import boot_page, call_api, page_header, render_footer, section
from display import scenario_label
from i18n import t

st.set_page_config(
    page_title="LastMile Lab: ViennaCart CVRP Dispatch Planner",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

boot_page()

page_header(t("home.title"), t("home.subtitle"), kicker=t("home.kicker"))

health = call_api(get_health)
status_cols = st.columns(3)
status_cols[0].metric(
    t("home.api"),
    t("home.api.on") if health else t("home.api.off"),
    help=t("home.api.help"),
)
status_cols[1].metric(
    t("home.scenario"),
    scenario_label(st.session_state.scenario_id),
    help=t("home.scenario.help"),
)
status_cols[2].metric(
    t("home.model"),
    t("home.model.value"),
    help=t("home.model.help"),
)

if health is None:
    st.error(t("home.offline"))

with st.expander(t("home.about")):
    st.markdown(t("synthetic.notice"))
    st.markdown(t("home.about.body"))
    st.caption(f"{t('home.tech.endpoint')}: `{backend_url()}`")
    st.caption(f"{t('home.tech.scenario')}: `{st.session_state.scenario_id}`")

section(t("home.what"), t("home.what.cap"))
st.markdown(t("home.what.body"))

section(t("home.walk"), t("home.walk.cap"))
steps = st.columns(4)
steps[0].markdown(
    f'<div class="lm-card"><h3>{t("home.s1.title")}</h3><p>{t("home.s1.body")}</p></div>',
    unsafe_allow_html=True,
)
steps[1].markdown(
    f'<div class="lm-card"><h3>{t("home.s2.title")}</h3><p>{t("home.s2.body")}</p></div>',
    unsafe_allow_html=True,
)
steps[2].markdown(
    f'<div class="lm-card"><h3>{t("home.s3.title")}</h3><p>{t("home.s3.body")}</p></div>',
    unsafe_allow_html=True,
)
steps[3].markdown(
    f'<div class="lm-card"><h3>{t("home.s4.title")}</h3><p>{t("home.s4.body")}</p></div>',
    unsafe_allow_html=True,
)

cta1, cta2 = st.columns(2)
with cta1:
    if st.button(t("home.cta1"), type="primary", use_container_width=True):
        st.switch_page("pages/1_Dispatch_Setup.py")
with cta2:
    if st.button(t("home.cta2"), use_container_width=True):
        st.switch_page("pages/5_Learning_Lab.py")

section(t("home.pages"), t("home.pages.cap"))
pages = [
    (t("nav.dispatch"), t("home.p1")),
    (t("nav.routes"), t("home.p2")),
    (t("nav.compare"), t("home.p3")),
    (t("nav.inspect"), t("home.p4")),
    (t("nav.learn"), t("home.p5")),
]
for label, blurb in pages:
    st.markdown(f"**{label}.** {blurb}")

section(t("home.not"))
st.markdown(t("home.not.body"))

render_footer()
