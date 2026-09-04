"""Shared Streamlit layout. Display only; no solver or KPI formulae."""

from __future__ import annotations

import re
from collections.abc import Callable
from html import escape
from typing import Any

import streamlit as st

from api_client import ApiError, backend_url, get_health
from display import (
    VEHICLE_COLOURS,
    display_node,
    format_km,
    format_pct,
    humanize_check_message,
    scenario_label,
    vehicle_colour,
)
from i18n import t
from state import ensure_session

THEME_CSS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700&display=swap");

:root {
  --lm-canvas: #F4F7FA;
  --lm-surface: rgba(255, 255, 255, 0.96);
  --lm-surface-soft: #EDF2F6;
  --lm-ink: #172B3A;
  --lm-muted: #526477;
  --lm-navy: #16324F;
  --lm-navy-2: #204B68;
  --lm-teal: #0F766E;
  --lm-border: #D7E0E8;
  --lm-shadow: 0 8px 24px rgba(20, 45, 68, 0.07);
}
html, body, [class*="css"] {
  font-family: "Inter", "Segoe UI", system-ui, sans-serif;
}
[data-testid="stAppViewContainer"], .stApp { background: var(--lm-canvas); }
.block-container {
  padding-top: 0.35rem;
  padding-bottom: 2.4rem;
  padding-left: 1.2rem;
  padding-right: 1.2rem;
  max-width: 1560px;
}
[data-testid="stAppToolbar"],
.stAppToolbar {
  display: none !important;
}
header[data-testid="stHeader"],
div[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
  opacity: 0 !important;
  pointer-events: none !important;
  background: transparent !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}
#MainMenu, footer { visibility: hidden; }

[data-testid="stSidebar"] {
  background: #13293D;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}
[data-testid="stSidebar"] * { color: #F7FAFC !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255, 255, 255, 0.12); }
[data-testid="stSidebar"] .stPageLink a {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 0.42rem 0.65rem;
  margin-bottom: 0.18rem;
  font-size: 0.92rem;
  line-height: 1.3;
}
[data-testid="stSidebar"] .stPageLink a:hover {
  border-color: rgba(129, 230, 217, 0.35);
  background: rgba(255, 255, 255, 0.07);
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 9px;
}

.lm-brand {
  display: flex; gap: 0.72rem; align-items: center;
  margin: 0.2rem 0 0.9rem 0;
}
.lm-mark {
  width: 40px; height: 40px; border-radius: 9px;
  background: rgba(15, 118, 110, 0.2); color: #99F6E4;
  border: 1px solid rgba(153, 246, 228, 0.42);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; letter-spacing: 0.04em; font-size: 0.78rem;
}
.lm-name { font-size: 1.08rem; font-weight: 650; line-height: 1.1; }
.lm-sub { font-size: 0.82rem; opacity: 0.82; margin-top: 0.12rem; }

.lm-hero {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 190px;
  align-items: center;
  min-height: 0;
  background:
    radial-gradient(circle at 88% 20%, rgba(52, 211, 153, 0.16), transparent 30%),
    linear-gradient(135deg, #102A43 0%, #173F5F 68%, #165E63 128%);
  color: #F8FAFC;
  border-radius: 14px;
  padding: 1.35rem 1.7rem;
  margin-bottom: 0.85rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: var(--lm-shadow);
}
.lm-hero::after {
  content: "";
  position: absolute;
  width: 270px; height: 270px; right: -120px; bottom: -170px;
  border: 1px solid rgba(255, 255, 255, 0.13);
  border-radius: 50%;
}
.lm-hero-content { position: relative; z-index: 2; }
.lm-hero h1 {
  font-size: clamp(1.75rem, 3vw, 2.35rem);
  font-weight: 650;
  letter-spacing: -0.035em;
  line-height: 1.12;
  margin: 0 0 0.7rem 0;
  color: #FFFFFF;
  overflow-wrap: anywhere;
}
.lm-hero p {
  margin: 0;
  color: #D9E4EC;
  max-width: 48rem;
  line-height: 1.58;
  font-size: 0.97rem;
}
.lm-kicker {
  color: #99F6E4;
  font-size: 0.74rem;
  letter-spacing: 0.095em;
  text-transform: uppercase;
  font-weight: 650;
  margin-bottom: 0.65rem;
}
.lm-route-motif { position: relative; height: 116px; opacity: 0.8; }
.lm-route-motif::before {
  content: "";
  position: absolute;
  inset: 31px 20px 28px 12px;
  border-top: 2px solid rgba(153, 246, 228, 0.52);
  border-right: 2px solid rgba(153, 246, 228, 0.52);
  transform: skewY(-19deg);
}
.lm-route-motif span {
  position: absolute;
  width: 13px; height: 13px;
  background: #99F6E4;
  border: 3px solid rgba(16, 42, 67, 0.82);
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(153, 246, 228, 0.17);
}
.lm-route-motif span:nth-child(1) { left: 10px; bottom: 22px; }
.lm-route-motif span:nth-child(2) { left: 76px; top: 20px; }
.lm-route-motif span:nth-child(3) { right: 16px; bottom: 34px; }

.lm-section {
  margin: 1rem 0 0.45rem 0;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--lm-border);
}
.lm-section h2 {
  font-size: 1.22rem;
  font-weight: 650;
  letter-spacing: -0.015em;
  margin: 0;
  color: var(--lm-navy);
}
.lm-section p { margin: 0.28rem 0 0 0; color: var(--lm-muted); font-size: 0.88rem; }
.lm-callout {
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid var(--lm-border);
  border-left: 4px solid var(--lm-teal);
  border-radius: 10px;
  padding: 0.9rem 1rem;
  margin: 0.55rem 0 0.75rem;
  box-shadow: 0 3px 12px rgba(20, 45, 68, 0.04);
  font-size: 0.95rem;
  line-height: 1.55;
  color: var(--lm-ink);
}
.lm-callout p { margin: 0; }
.lm-util-caption {
  font-size: 0.75rem;
  font-weight: 650;
  color: var(--lm-muted);
  margin: 0.75rem 0 0.28rem;
  letter-spacing: 0.03em;
}
.lm-glossary p {
  margin: 0 0 0.72rem 0;
  padding: 0;
  font-size: 0.84rem;
  line-height: 1.45;
  color: #F7FAFC;
  text-indent: 0;
}
.lm-glossary p:last-child { margin-bottom: 0; }
.lm-glossary strong { font-weight: 650; }
.lm-card {
  background: var(--lm-surface);
  border: 1px solid var(--lm-border);
  border-radius: 11px;
  padding: 1rem;
  height: 100%;
  box-shadow: 0 3px 14px rgba(20, 45, 68, 0.045);
}
.lm-card h3 { margin: 0 0 0.35rem; color: var(--lm-navy); font-size: 1rem; }
.lm-card p { margin: 0; color: var(--lm-muted); font-size: 0.88rem; line-height: 1.5; }
.lm-empty {
  background: var(--lm-surface);
  border: 1px dashed #A9B8C5;
  border-radius: 11px;
  padding: 1.35rem 1.1rem;
  text-align: center;
  color: var(--lm-muted);
}
.lm-pill {
  display: inline-block;
  border-radius: 999px;
  padding: 0.22rem 0.66rem;
  font-size: 0.78rem;
  font-weight: 650;
  letter-spacing: 0.01em;
}
.lm-footer {
  margin-top: 2rem;
  color: var(--lm-muted);
  font-size: 0.875rem;
  border-top: 1px solid var(--lm-border);
  padding-top: 0.8rem;
}
.lm-vehicle-card {
  --vehicle-accent: #0F766E;
  background:
    linear-gradient(
      90deg,
      color-mix(in srgb, var(--vehicle-accent) 6%, #FFFFFF) 0,
      #FFFFFF 34%
    );
  border: 1px solid var(--lm-border);
  border-left: 5px solid var(--vehicle-accent);
  border-radius: 11px;
  padding: 0.72rem 0.9rem;
  margin: 0.45rem 0;
  box-shadow: 0 4px 16px rgba(20, 45, 68, 0.055);
}
.lm-vehicle-head {
  display: flex; justify-content: space-between; align-items: center; gap: 0.8rem;
  margin-bottom: 0.22rem;
}
.lm-vehicle-head h3 {
  margin: 0; color: var(--vehicle-accent); font-size: 1rem; font-weight: 700;
}
.lm-vehicle-tag {
  background: var(--lm-surface-soft); color: var(--lm-navy);
  border-radius: 999px; padding: 0.2rem 0.55rem;
  font-size: 0.76rem; font-weight: 600;
}
.lm-vehicle-grid {
  display: grid; grid-template-columns: repeat(3, minmax(110px, 1fr));
  gap: 0.48rem 1.2rem; margin: 0;
}
.lm-vehicle-grid div { min-width: 0; }
.lm-vehicle-grid .lm-route-cell { grid-column: 1 / -1; }
.lm-vehicle-grid dt {
  color: var(--lm-muted); font-size: 0.72rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.055em; margin-bottom: 0.08rem;
}
.lm-vehicle-grid dd {
  margin: 0; color: var(--lm-ink); font-size: 0.87rem;
  line-height: 1.4; overflow-wrap: anywhere; word-break: break-word;
}
.lm-route {
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
}
.lm-util-head {
  display: flex; justify-content: space-between; gap: 0.75rem;
  color: var(--lm-muted); font-size: 0.76rem; line-height: 1.25;
  margin-top: 0.52rem;
}
.lm-util-head strong { color: var(--lm-ink); font-weight: 650; }
.lm-util-track {
  height: 5px; background: #DFE7ED; border-radius: 999px;
  margin-top: 0.25rem; overflow: hidden;
}
.lm-util-fill { height: 100%; background: var(--vehicle-accent); border-radius: inherit; }
.lm-vehicle-note { color: var(--lm-muted); font-size: 0.8rem; margin: 0.35rem 0 0; }

.lm-table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--lm-border);
  border-radius: 9px;
  background: #FFFFFF;
  margin: 0.35rem 0 0.65rem;
}
.lm-table {
  width: 100%;
  border-collapse: collapse;
  color: var(--lm-ink);
  font-size: 0.88rem;
  line-height: 1.35;
}
.lm-table th, .lm-table td {
  padding: 0.52rem 0.65rem;
  border-right: 1px solid #E4EAF0;
  border-bottom: 1px solid #E4EAF0;
  text-align: left;
  vertical-align: top;
  white-space: normal;
}
.lm-table thead th {
  background: #EAF0F4;
  color: #111827;
  font-weight: 700;
  font-size: 0.92rem;
  white-space: nowrap;
}
.lm-table tbody th {
  color: #111827;
  font-weight: 650;
  background: #F8FAFC;
}
.lm-table .lm-num {
  text-align: left;
  font-variant-numeric: tabular-nums;
}
.lm-table tr:last-child th, .lm-table tr:last-child td { border-bottom: 0; }
.lm-table th:last-child, .lm-table td:last-child { border-right: 0; }

.lm-tech-list { margin: 0; width: 100%; }
.lm-tech-item { margin: 0 0 0.7rem; }
.lm-tech-item:last-child { margin-bottom: 0.15rem; }
.lm-tech-list dt {
  margin: 0;
  color: #F7FAFC !important;
  font-size: 0.8rem;
  font-weight: 650;
  letter-spacing: 0;
  text-transform: none;
}
.lm-tech-hint {
  display: block;
  margin: 0.12rem 0 0.22rem;
  color: #B8C7D4 !important;
  font-size: 0.72rem;
  line-height: 1.35;
}
.lm-tech-list dd { margin: 0; }
.lm-tech-value {
  display: block;
  width: 100%;
  box-sizing: border-box;
  padding: 0.4rem 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.08);
  color: #FFFFFF !important;
  font-family: "Cascadia Code", Consolas, monospace;
  font-size: 0.74rem;
  line-height: 1.4;
  overflow-wrap: anywhere;
  word-break: break-word;
}
.lm-tech-help {
  color: #B8C7D4 !important;
  font-size: 0.72rem;
  line-height: 1.4;
  margin: 0.55rem 0 0;
}

div[data-testid="stMetric"] {
  background: var(--lm-surface);
  border: 1px solid var(--lm-border);
  border-radius: 10px;
  padding: 0.72rem 0.85rem;
  box-shadow: 0 3px 14px rgba(20, 45, 68, 0.045);
}
div[data-testid="stMetricLabel"] { color: var(--lm-muted); }
div[data-testid="stMetricValue"] {
  font-size: 1.05rem;
  color: var(--lm-navy);
  white-space: normal !important;
  overflow-wrap: anywhere;
  line-height: 1.28;
}
div[data-testid="stMetricDelta"] { font-size: 0.78rem; }

.stButton > button, .stDownloadButton > button {
  border-radius: 8px !important;
  font-weight: 600 !important;
  letter-spacing: 0;
  min-height: 2.75rem;
  padding: 0.46rem 0.95rem !important;
  border: 1px solid var(--lm-navy) !important;
  transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: var(--lm-teal) !important;
  box-shadow: 0 3px 10px rgba(15, 118, 110, 0.13);
}
.stButton > button[kind="primary"] {
  background: var(--lm-navy) !important;
  color: #FFFFFF !important;
}
.stButton > button[kind="secondary"], .stButton > button[kind="tertiary"] {
  background: rgba(255, 255, 255, 0.92) !important;
  color: var(--lm-navy) !important;
}
.lm-lang-wrap {
  display: flex;
  justify-content: flex-end;
  margin: 0 0 -2.85rem 0;
  position: relative;
  z-index: 60;
}
.lm-lang [data-testid="stPopover"] > div > button,
div[data-testid="stPopover"] > div > button {
  min-height: 2.35rem !important;
  padding: 0.28rem 0.7rem !important;
  border: 1px solid var(--lm-navy) !important;
  background: #FFFFFF !important;
  color: var(--lm-navy) !important;
  font-weight: 650 !important;
  opacity: 1 !important;
  box-shadow: 0 1px 4px rgba(20, 45, 68, 0.12) !important;
}
button:focus-visible, a:focus-visible, input:focus-visible,
[role="radio"]:focus-visible {
  outline: 3px solid rgba(37, 99, 235, 0.45) !important;
  outline-offset: 2px !important;
}
[data-testid="stCaptionContainer"] { font-size: 0.875rem; }
div[data-testid="stDataFrame"] {
  border: 1px solid var(--lm-border);
  border-radius: 9px;
  overflow: hidden;
  background: var(--lm-surface);
}
div[data-testid="stDataFrame"] [role="gridcell"],
div[data-testid="stDataFrame"] [role="columnheader"] {
  text-align: left !important;
  justify-content: flex-start !important;
}
@media (max-width: 760px) {
  .lm-hero { grid-template-columns: 1fr; padding: 1.4rem; min-height: auto; }
  .lm-route-motif { display: none; }
  .lm-vehicle-grid { grid-template-columns: 1fr; }
  .lm-vehicle-grid .lm-route-cell { grid-column: 1; }
  .lm-lang-wrap { margin-bottom: 0.4rem; }
}
</style>
"""


def _vehicle_colour_css() -> str:
    rules: list[str] = []
    for index, colour in enumerate(VEHICLE_COLOURS, start=1):
        cls = f"lm-v{index:02d}"
        rules.append(
            f".lm-vehicle-card.{cls}{{--vehicle-accent:{colour};border-left-color:{colour};}}"
            f".lm-vehicle-card.{cls} .lm-vehicle-head h3{{color:{colour};}}"
            f".lm-vehicle-card.{cls} .lm-util-fill{{background:{colour};}}"
        )
    return "".join(rules)


def vehicle_theme_class(vehicle_id: str) -> str:
    colour = vehicle_colour(vehicle_id)
    try:
        index = VEHICLE_COLOURS.index(colour)
    except ValueError:
        index = 0
    return f"lm-v{index + 1:02d}"


def _route_html(sequence: list[str]) -> str:
    return " -&gt;<wbr> ".join(escape(display_node(node_id)) for node_id in sequence)


def inject_theme() -> None:
    st.markdown(
        THEME_CSS.replace("</style>", _vehicle_colour_css() + "</style>"),
        unsafe_allow_html=True,
    )


def boot_page() -> None:
    ensure_session()
    inject_theme()
    render_language_bar()
    render_sidebar()


def _rich_inline(text: str) -> str:
    parts = re.split(r"(\*\*.+?\*\*)", text)
    rendered: list[str] = []
    for part in parts:
        if part.startswith("**") and part.endswith("**") and len(part) >= 4:
            rendered.append(f"<strong>{escape(part[2:-2])}</strong>")
        else:
            rendered.append(escape(part).replace("\n", "<br/>"))
    return "".join(rendered)


def _rich_html(text: str) -> str:
    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
    if not blocks:
        return ""
    return "".join(f"<p>{_rich_inline(block)}</p>" for block in blocks)


def render_language_bar() -> None:
    ensure_session()
    current = st.session_state.get("ui_language", "en").upper()
    st.markdown('<div class="lm-lang-wrap"><div class="lm-lang">', unsafe_allow_html=True)
    _spacer, right = st.columns([0.88, 0.12])
    with right:
        with st.popover(f"🌐 {current}", help=t("lang.help")):
            st.radio(
                t("lang.label"),
                options=["en", "de"],
                format_func=lambda code: "English" if code == "en" else "Deutsch",
                key="ui_language",
            )
    st.markdown("</div></div>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str, *, kicker: str | None = None) -> None:
    kicker_html = f'<div class="lm-kicker">{kicker}</div>' if kicker else ""
    st.markdown(
        f"""
        <div class="lm-hero">
          <div class="lm-hero-content">
            {kicker_html}
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>
          <div class="lm-route-motif" aria-hidden="true">
            <span></span><span></span><span></span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, caption: str | None = None) -> None:
    caption_html = f"<p>{caption}</p>" if caption else ""
    st.markdown(
        f'<div class="lm-section"><h2>{title}</h2>{caption_html}</div>',
        unsafe_allow_html=True,
    )


def callout(text: str) -> None:
    st.markdown(f'<div class="lm-callout">{_rich_html(text)}</div>', unsafe_allow_html=True)


def static_table(
    rows: list[dict[str, Any]],
    *,
    numeric_columns: set[str] | None = None,
    row_header: str | None = None,
) -> None:
    """Render a read-only table with stable alignment and accessible row headers."""
    if not rows:
        return
    columns = list(rows[0])
    if numeric_columns is None:
        numeric = {
            column
            for column in columns
            if any(row.get(column) is not None for row in rows)
            and all(
                value is None
                or (isinstance(value, int | float) and not isinstance(value, bool))
                for value in (row.get(column) for row in rows)
            )
        }
    else:
        numeric = numeric_columns
    head = "".join(
        f'<th class="{"lm-num" if column in numeric else ""}" scope="col">'
        f"{escape(str(column))}</th>"
        for column in columns
    )
    body_rows: list[str] = []
    for row in rows:
        cells: list[str] = []
        for column in columns:
            value = row.get(column)
            display = "" if value is None else str(value)
            css_class = "lm-num" if column in numeric else ""
            if column == row_header:
                cells.append(
                    f'<th class="{css_class}" scope="row">{escape(display)}</th>'
                )
            else:
                cells.append(f'<td class="{css_class}">{escape(display)}</td>')
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    html = (
        '<div class="lm-table-wrap"><table class="lm-table">'
        f"<thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody></table></div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def empty_state(title: str, body: str) -> None:
    st.markdown(
        f'<div class="lm-empty"><strong>{title}</strong><br/>{body}</div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Dispatch_Setup.py", label=t("empty.open"), icon="▶️")


def render_check_table(checks: list[dict[str, Any]]) -> None:
    rows = []
    for check in checks:
        code = str(check.get("code") or "")
        number = code.replace("CHECK_", "") if code.startswith("CHECK_") else code
        name_key = f"check.{code}"
        plain = t(name_key)
        if plain == name_key:
            plain = str(check.get("name") or code)
        rows.append(
            {
                t("check.col.check"): t("check.num", n=number),
                t("check.col.name"): plain,
                t("check.col.result"): t("check.ok") if check.get("passed") else t("check.fail"),
                t("check.col.stops"): (
                    t("check.stops_yes") if check.get("hard_fail") else t("check.stops_no")
                ),
                t("check.col.detail"): humanize_check_message(check),
            }
        )
    static_table(rows, row_header=t("check.col.check"))


def render_sidebar() -> None:
    ensure_session()
    with st.sidebar:
        st.markdown(
            f"""
            <div class="lm-brand">
              <div class="lm-mark">LM</div>
              <div>
                <div class="lm-name">LastMile Lab</div>
                <div class="lm-sub">{t("brand.sub")}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            get_health()
            st.markdown(
                f'<span class="lm-pill" style="background:#15803D;">{t("api.connected")}</span>',
                unsafe_allow_html=True,
            )
        except ApiError:
            st.markdown(
                f'<span class="lm-pill" style="background:#B42318;">{t("api.offline")}</span>',
                unsafe_allow_html=True,
            )
        st.divider()
        st.page_link("Home.py", label=t("nav.home"), icon="🏠")
        st.page_link("pages/1_Dispatch_Setup.py", label=t("nav.dispatch"), icon="📋")
        st.page_link("pages/2_Route_Plan.py", label=t("nav.routes"), icon="🗺️")
        st.page_link("pages/3_Baseline_vs_Optimised.py", label=t("nav.compare"), icon="📊")
        st.page_link("pages/4_Model_Inspector.py", label=t("nav.inspect"), icon="🔎")
        st.page_link("pages/5_Learning_Lab.py", label=t("nav.learn"), icon="🎓")
        st.divider()
        st.caption(f"{t('nav.scenario')}: {scenario_label(st.session_state.scenario_id)}")
        with st.expander(t("nav.glossary")):
            st.markdown(
                f'<div class="lm-glossary">{_rich_html(t("glossary.body"))}</div>',
                unsafe_allow_html=True,
            )
        with st.expander(t("nav.technical")):
            details = [
                (t("tech.endpoint"), t("tech.endpoint.hint"), backend_url()),
                (t("tech.scenario"), t("tech.scenario.hint"), st.session_state.scenario_id),
                (
                    t("tech.baseline"),
                    t("tech.baseline.hint"),
                    st.session_state.baseline_run_id or t("tech.not_generated"),
                ),
                (
                    t("tech.optimised"),
                    t("tech.optimised.hint"),
                    st.session_state.optimised_run_id or t("tech.not_generated"),
                ),
            ]
            items = "".join(
                "<div class='lm-tech-item'>"
                f"<dt>{escape(label)}</dt>"
                f"<span class='lm-tech-hint'>{escape(hint)}</span>"
                f"<dd><span class='lm-tech-value'>{escape(str(value))}</span></dd>"
                "</div>"
                for label, hint, value in details
            )
            st.markdown(
                f'<dl class="lm-tech-list">{items}</dl>'
                f'<p class="lm-tech-help">{escape(t("tech.help"))}</p>',
                unsafe_allow_html=True,
            )
        with st.expander(t("home.about")):
            st.caption(t("synthetic.notice"))


def render_footer() -> None:
    st.markdown(
        f'<div class="lm-footer">{t("footer")}</div>',
        unsafe_allow_html=True,
    )


def call_api(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    try:
        return func(*args, **kwargs)
    except ApiError as exc:
        if exc.kind == "connection":
            st.error(str(exc))
            st.caption(
                "In PowerShell: "
                r".\.venv\Scripts\python.exe -m uvicorn app.main:app "
                "--app-dir backend --host 127.0.0.1 --port 8000"
            )
        elif exc.kind == "timeout":
            st.warning(str(exc))
        elif exc.kind == "not_found":
            st.error(str(exc))
            st.caption(t("api.reconnect"))
        elif exc.kind == "server":
            st.error(t("api.server"))
            st.caption(str(exc))
        else:
            st.error(str(exc))
        return None


def export_buttons(run_id: str) -> None:
    from api_client import export_run

    with st.expander(t("export.title"), expanded=False):
        st.caption(t("export.cap"))
        col_json, col_csv = st.columns(2)
        with col_json:
            payload = call_api(export_run, run_id, "json")
            if payload is not None:
                content, mime, name = payload
                st.download_button(
                    t("export.json"),
                    data=content,
                    file_name=name,
                    mime=mime,
                    key=f"export-json-{run_id}",
                    help=t("export.cap"),
                )
        with col_csv:
            payload = call_api(export_run, run_id, "csv")
            if payload is not None:
                content, mime, name = payload
                st.download_button(
                    t("export.csv"),
                    data=content,
                    file_name=name,
                    mime=mime,
                    key=f"export-csv-{run_id}",
                    help=t("export.cap"),
                )


def status_badge(status: str | None, *, scenario_id: str | None = None) -> None:
    if not status:
        st.info(t("status.none"))
        return
    label_key = f"status.{status}.label"
    hint_key = f"status.{status}.hint"
    label = t(label_key)
    hint = t(hint_key)
    active = scenario_id or st.session_state.get("scenario_id")
    if status == "feasible" and active == "LEARNING_6":
        hint = t("status.feasible.hint.learning_6")
    if label == label_key:
        label = status.replace("_", " ")
        hint = t("status.unknown")
    colours = {
        "feasible": ("#0F6B5D", "#E8F5F1"),
        "heuristic_incomplete": ("#8A4B08", "#FFF4E5"),
        "no_solution_found": ("#8A4B08", "#FFF4E5"),
        "infeasible": ("#A12B2B", "#FDECEC"),
        "invalid": ("#A12B2B", "#FDECEC"),
        "error": ("#A12B2B", "#FDECEC"),
        "pending": ("#204B68", "#EAF1F6"),
        "passed": ("#0F6B5D", "#E8F5F1"),
    }
    fg, bg = colours.get(status, ("#204B68", "#EAF1F6"))
    st.markdown(
        f'<span class="lm-pill" style="background:{bg};color:{fg};border:1px solid {fg};">'
        f"{label}</span>",
        unsafe_allow_html=True,
    )
    st.caption(hint)


def vehicle_card(vehicle: dict[str, Any]) -> None:
    utilisation = vehicle.get("capacity_utilisation")
    used = vehicle.get("is_used")
    title = f"{t('van.label')} {vehicle['vehicle_id']}"
    if not used:
        title += f" ({t('van.unused')})"

    accent = vehicle_theme_class(vehicle["vehicle_id"])
    if used and vehicle.get("sequence"):
        utilisation_value = min(max(float(utilisation or 0.0), 0.0), 1.0)
        content = (
            f"<div class='lm-vehicle-card {accent}'>"
            "<div class='lm-vehicle-head'>"
            f"<h3>{escape(title)}</h3>"
            f"<span class='lm-vehicle-tag'>{escape(format_pct(utilisation))} "
            f"{escape(t('van.util.short'))}</span>"
            "</div>"
            "<dl class='lm-vehicle-grid'>"
            f"<div class='lm-route-cell'><dt>{escape(t('van.route'))}</dt>"
            f"<dd class='lm-route'>{_route_html(vehicle['sequence'])}</dd></div>"
            f"<div><dt>{escape(t('van.orders'))}</dt>"
            f"<dd>{vehicle['customer_count']}</dd></div>"
            f"<div><dt>{escape(t('van.load'))}</dt>"
            f"<dd>{vehicle['assigned_demand_totes']} / {vehicle['capacity_totes']} "
            f"{escape(t('tote.word'))}</dd></div>"
            f"<div><dt>{escape(t('van.distance'))}</dt>"
            f"<dd>{escape(format_km(vehicle.get('route_distance_metres')))}</dd></div>"
            "</dl>"
            "<div class='lm-util-head'>"
            f"<span>{escape(t('van.util'))}</span>"
            f"<strong>{vehicle['assigned_demand_totes']} / {vehicle['capacity_totes']} "
            f"{escape(t('tote.word'))}</strong></div>"
            "<div class='lm-util-track' role='progressbar' "
            f"aria-label='{escape(t('van.util'))}' "
            f"title='{escape(t('van.util.hint'))}' "
            f"aria-valuenow='{utilisation_value * 100:.1f}' aria-valuemin='0' aria-valuemax='100'>"
            f"<div class='lm-util-fill' style='width:{utilisation_value * 100:.1f}%'></div>"
            "</div>"
            "</div>"
        )
    else:
        content = (
            f"<div class='lm-vehicle-card {accent}'>"
            f"<div class='lm-vehicle-head'><h3>{escape(title)}</h3></div>"
            f"<p class='lm-vehicle-note'>{escape(t('van.idle'))}</p>"
            "<dl class='lm-vehicle-grid'>"
            f"<div><dt>{escape(t('van.capacity'))}</dt>"
            f"<dd>{vehicle['capacity_totes']} {escape(t('tote.word'))}</dd></div>"
            "</dl></div>"
        )
    st.markdown(content, unsafe_allow_html=True)
