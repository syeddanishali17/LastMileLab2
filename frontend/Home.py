"""Entry point and explicit page registry for the planning journey."""

from pathlib import Path

import streamlit as st

from components import boot_page, inject_theme
from i18n import t
from state import ensure_session

BRAND_MARK = Path(__file__).resolve().parent / "assets" / "brand.svg"

# Session state only: nothing may render before st.set_page_config below.
ensure_session()
page = st.navigation(
    {
        t("nav.workflow"): [
            st.Page(
                "pages/0_Overview.py",
                title=t("nav.home"),
                default=True,
            ),
            st.Page("pages/1_Dispatch_Setup.py", title=t("nav.dispatch"), url_path="scenarios"),
            st.Page("pages/3_Baseline_vs_Optimised.py", title=t("nav.compare"), url_path="plan"),
        ],
        t("nav.secondary"): [
            st.Page("pages/6_Methodology.py", title=t("nav.method"), url_path="methodology"),
            st.Page("pages/4_Model_Inspector.py", title=t("nav.inspect"), url_path="validation"),
        ],
    },
    position="sidebar",
)
# Configured after navigation resolves, so the browser tab names the current page
# ("Scenarios · LastMile Lab") and shows the brand mark instead of Streamlit's icon.
st.set_page_config(
    page_title=f"{page.title} · LastMile Lab",
    page_icon=str(BRAND_MARK) if BRAND_MARK.exists() else None,
    layout="wide",
    initial_sidebar_state="auto",
)
inject_theme()
if BRAND_MARK.exists():
    st.logo(str(BRAND_MARK), size="medium")
boot_page()
page.run()
