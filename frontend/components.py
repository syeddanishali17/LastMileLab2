"""Shared Streamlit layout. Display only; no solver or KPI formulae."""

from __future__ import annotations

import re
from collections.abc import Callable
from html import escape
from typing import Any

import streamlit as st

from api_client import ApiError
from display import (
    VEHICLE_COLOURS,
    display_node,
    format_km,
    format_pct,
    humanize_check_message,
    vehicle_colour,
)
from i18n import current_language, t
from state import ensure_session

THEME_CSS = """
<style>

:root {
  --lm-font: "Source Sans Pro", "Segoe UI", system-ui, sans-serif;
  --lm-text: 1rem;
  --lm-small: 0.875rem;
  --lm-caption: 0.8125rem;
  --lm-canvas: #F6F8FA;
  --lm-surface: #FFFFFF;
  --lm-surface-soft: #F1F5F8;
  --lm-ink: #17212B;
  --lm-muted: #586879;
  --lm-navy: #173B57;
  --lm-navy-2: #1B4059;
  --lm-teal: #0F766E;
  --lm-accent: #4FD1C5;
  --lm-border: #D9E1E8;
  --lm-shadow: 0 2px 8px rgba(16, 42, 58, 0.06);
  --lm-sidebar: #102A3A;
  --lm-success: #087A5A;
  --lm-warning: #A86510;
  --lm-danger: #B42318;
  --lm-focus: #2563EB;
}
html, body, .stApp, .stApp button, .stApp input, .stApp textarea,
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] :is(h1, h2, h3) {
  font-family: var(--lm-font);
}
/* Native heading padding otherwise inflates every custom card and page title. */
:is(.lm-hero, .lm-inner, .lm-section, .lm-card) :is(h1, h2, h3) {
  padding: 0;
}
.stMarkdown p { max-width: 72ch; font-size: var(--lm-text); line-height: 1.55; }
[data-testid="stAppViewContainer"], .stApp { background: var(--lm-canvas); }
section.main,
[data-testid="stMain"] {
  padding-left: 0 !important;
  padding-top: 0 !important;
  margin-top: 0 !important;
}
[data-testid="stAppViewContainer"] {
  padding-top: 0 !important;
}
.block-container,
[data-testid="stMainBlockContainer"] {
  padding-top: 24px !important;
  padding-bottom: 2rem;
  padding-left: 28px !important;
  padding-right: 28px !important;
  max-width: none !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
}
[data-testid="stMainBlockContainer"] > div:first-child {
  padding-top: 0 !important;
  margin-top: 0 !important;
}
[data-testid="stAppToolbar"],
.stAppToolbar,
.stAppHeader,
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stDeployButton"],
.stDeployButton,
.stAppDeployButton {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
}
[data-testid="stElementContainer"]:has(style),
[data-testid="stMarkdownContainer"]:has(style) {
  display: none !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}
#MainMenu, footer { visibility: hidden; }

[data-testid="stSidebar"] {
  background: var(--lm-sidebar);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}
section[data-testid="stSidebar"][aria-expanded="true"] {
  width: 272px !important;
  min-width: 272px !important;
  max-width: 272px !important;
  flex: 0 0 272px !important;
}
section[data-testid="stSidebar"][aria-expanded="true"] > div:first-child,
section[data-testid="stSidebar"][aria-expanded="true"] [data-testid="stSidebarContent"] {
  width: 272px !important;
  min-width: 272px !important;
  max-width: 272px !important;
}
section[data-testid="stSidebar"] > div:first-child {
  padding: 8px 0 1rem;
}
[data-testid="stSidebarHeader"] {
  position: relative;
  display: grid !important;
  grid-template-columns: 40px minmax(0, 1fr) auto;
  grid-template-rows: auto auto;
  column-gap: 10px;
  align-items: center;
  padding: 8px 16px 10px 24px !important;
  margin: 0 !important;
}
[data-testid="stLogo"],
[data-testid="stLogo"] > div,
[data-testid="stHeaderLogo"] {
  display: block !important;
  grid-column: 1;
  grid-row: 1 / span 2;
  width: 40px !important;
  height: 40px !important;
  overflow: visible !important;
  border-radius: 8px !important;
  clip-path: none !important;
}
[data-testid="stLogo"] *,
[data-testid="stHeaderLogo"] * {
  border-radius: 8px !important;
  clip-path: none !important;
}
[data-testid="stLogo"] img,
[data-testid="stSidebarHeader"] img {
  width: 40px !important;
  height: 40px !important;
  max-width: 40px !important;
  max-height: 40px !important;
  border-radius: 8px !important;
  object-fit: contain !important;
  clip-path: none !important;
}
[data-testid="stSidebarHeader"]::before {
  grid-column: 2;
  grid-row: 1;
  content: "LastMile Lab";
  font-size: 18px;
  font-weight: 600;
  line-height: 1.2;
  color: #F7FAFC;
}
[data-testid="stSidebarHeader"]::after {
  grid-column: 2;
  grid-row: 2;
  content: var(--lm-brand-sub, "CVRP route optimization");
  font-size: 13px;
  font-weight: 400;
  line-height: 1.25;
  opacity: 0.78;
  color: #F7FAFC;
  white-space: nowrap;
}
[data-testid="stSidebarHeader"] button,
[data-testid="stSidebarCollapseButton"],
[data-testid="stBaseButton-headerNoPadding"] {
  grid-column: 3;
  grid-row: 1 / span 2;
  align-self: start;
  justify-self: end;
  margin: 0 !important;
}
[data-testid="stSidebar"] * { color: #F7FAFC !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255, 255, 255, 0.12); }
[data-testid="stSidebarUserContent"] {
  flex: 0 0 auto !important;
  padding: 0 0 16px !important;
  margin-top: 4px !important;
}
[data-testid="stSidebarNav"] {
  padding: 0;
  margin: 0;
  flex: 0 0 auto !important;
}
[data-testid="stSidebarContent"] {
  display: flex !important;
  flex-direction: column !important;
  gap: 0 !important;
}
[data-testid="stSidebarNavItems"] { gap: 3px; }
[data-testid="stSidebarNavLink"] {
  border-radius: 0 !important;
  border-left: 3px solid transparent !important;
  padding: 9px 16px 9px 21px !important;
  margin: 0 !important;
  font-size: 16px !important;
  font-weight: 400 !important;
  line-height: 1.4 !important;
}
[data-testid="stSidebarNavLink"]:hover {
  background: rgba(255, 255, 255, 0.06) !important;
}
[data-testid="stSidebarNavLink"] span {
  font-size: 16px !important;
  white-space: nowrap;
}
[data-testid="stSidebarNavSeparator"],
[data-testid="stNavSectionHeader"],
[data-testid="stSidebarNav"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebarNav"] small,
[data-testid="stSidebarNav"] li div p {
  font-size: 13px !important;
  font-weight: 600 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  opacity: 0.72;
  margin: 12px 0 4px !important;
  padding: 0 24px !important;
}
[data-testid="stSidebarNav"] ul:first-of-type [data-testid="stNavSectionHeader"],
[data-testid="stSidebarNav"] li:first-child [data-testid="stMarkdownContainer"] p {
  margin-top: 8px !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"],
[data-testid="stSidebarNav"] a[aria-current="page"] {
  background: #1B4059 !important;
  border-left: 3px solid #4FD1C5 !important;
  box-shadow: none !important;
  font-weight: 600 !important;
  color: #FFFFFF !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"]::after,
[data-testid="stSidebarNav"] a[aria-current="page"]::after,
[data-testid="stSidebarNavLink"][aria-current="page"]::before,
[data-testid="stSidebarNav"] a[aria-current="page"]::before {
  content: none !important;
  display: none !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 9px;
}

.lm-brand {
  display: flex; gap: 10px; align-items: center;
  margin: 0 0 8px;
  padding: 0 18px;
}
.lm-mark {
  width: 40px; height: 40px; flex: 0 0 40px;
}
.lm-mark svg { display: block; width: 40px; height: 40px; }
.lm-name { font-size: 18px; font-weight: 600; line-height: 1.15; color: #FFFFFF; }
.lm-sub { font-size: 13px; opacity: 0.78; margin-top: 2px; font-weight: 400; }
.lm-lang-label {
  font-size: 13px; font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; opacity: 0.72; margin: 12px 0 4px; padding: 0 24px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] {
  padding: 0 24px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label,
[data-testid="stSidebar"] [data-testid="stRadio"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
  font-size: 16px !important;
}
.lm-api-status {
  font-size: 14px; opacity: 0.8; margin: 8px 0 0; padding: 0 24px;
}

.lm-hero {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px;
  align-items: center;
  min-height: 0;
  background:
    radial-gradient(circle at 88% 20%, rgba(52, 211, 153, 0.16), transparent 30%),
    linear-gradient(135deg, #102A43 0%, #173F5F 68%, #165E63 128%);
  color: #F8FAFC;
  border-radius: 14px;
  padding: 24px 28px;
  margin-top: 0;
  margin-bottom: 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: var(--lm-shadow);
  gap: 16px 24px;
}
.lm-hero::after {
  content: "";
  position: absolute;
  width: 270px; height: 270px; right: -120px; bottom: -170px;
  border: 1px solid rgba(255, 255, 255, 0.13);
  border-radius: 50%;
}
.lm-hero-heading, .lm-hero-copy { position: relative; z-index: 2; }
.lm-hero-copy { grid-column: 1 / -1; }
.lm-hero h1 {
  font-size: clamp(28px, 2.4vw, 34px);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.17;
  margin: 0;
  color: #FFFFFF;
  overflow-wrap: break-word;
}
.lm-hero p {
  margin: 0 0 12px 0;
  color: #D9E4EC;
  max-width: none;
  line-height: 1.55;
  font-size: var(--lm-text);
  font-weight: 400;
}
.lm-hero-copy p:not(.lm-hero-context):not(.lm-hero-author) {
  text-align: left;
}
.lm-hero p:last-child { margin-bottom: 0; }
.stMarkdown .lm-hero p { max-width: none; }
.lm-hero-context {
  color: #B7C9D4 !important;
  font-size: 14px !important;
  margin-top: 4px !important;
  text-align: left !important;
  text-align-last: left !important;
}
.lm-hero-author {
  color: #9BB0BD !important;
  font-size: 14px !important;
  margin-top: 8px !important;
  text-align: left !important;
  text-align-last: left !important;
}
.lm-kicker {
  color: #99F6E4;
  font-size: 14px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 12px;
}
.lm-route-motif {
  position: relative;
  z-index: 2;
  height: 123px;
  opacity: 0.96;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.lm-route-motif svg.lm-hero-mark { width: 123px; height: 123px; }
.lm-hero-depot {
  transform-box: fill-box;
  transform-origin: center;
  animation: lm-hero-depot 4s ease-in-out infinite;
}
.lm-hero-route {
  fill: none; stroke: #99F6E4; stroke-width: 1.5;
  stroke-dasharray: 4 8; stroke-dashoffset: 12;
  opacity: 0.55;
  animation: lm-hero-route 2s linear infinite;
}
.lm-hero-route.r2 { animation-delay: 0.2s; }
.lm-hero-route.r3 { animation-delay: 0.35s; }
.lm-hero-node {
  opacity: 0.45;
  animation: lm-hero-node 4s ease-in-out infinite;
}
.lm-hero-node.n2 { animation-delay: 0.15s; }
.lm-hero-node.n3 { animation-delay: 0.28s; }
@keyframes lm-hero-depot {
  0% { opacity: 0.7; transform: scale(1); }
  100% { opacity: 1; transform: scale(1); }
  22%, 72% { opacity: 1; transform: scale(1.06); }
}
@keyframes lm-hero-route {
  from { stroke-dashoffset: 12; opacity: 0.85; }
  to { stroke-dashoffset: 0; opacity: 0.85; }
}
@keyframes lm-hero-node {
  0%, 100% { opacity: 0.65; }
  50% { opacity: 1; }
}
.lm-section {
  margin: 1rem 0 0.45rem 0;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--lm-border);
}
.lm-section h2 {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.015em;
  margin: 0;
  color: var(--lm-navy);
}
.lm-section p { margin: 0.28rem 0 0 0; color: var(--lm-muted); font-size: 14px; }
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
.lm-card h3 {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 0 0 8px;
  color: var(--lm-navy);
  font-size: 18px;
  line-height: 1.3;
  font-weight: 600;
}
.lm-card p {
  margin: 0; color: var(--lm-muted); font-size: var(--lm-text); line-height: 1.55; font-weight: 400;
}
.lm-card-heading {
  position: relative;
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 8px; margin-bottom: 8px;
}
.lm-card-heading h3 { margin: 0; hyphens: auto; }
.lm-info { flex: 0 0 24px; }
.lm-info summary {
  display: flex; align-items: center; justify-content: center;
  width: 24px; height: 24px; padding: 0;
  list-style: none; cursor: pointer; color: var(--lm-muted);
  border-radius: 4px;
}
.lm-info summary::-webkit-details-marker { display: none; }
.lm-info summary:hover, .lm-info[open] summary { background: var(--lm-surface-soft); }
.lm-info summary svg { display: block; width: 16px; height: 16px; }
.lm-card .lm-info-text {
  position: absolute; top: calc(100% + 8px); left: 0; right: 0; z-index: 10;
  width: auto;
  padding: 12px; margin: 0; border: 1px solid var(--lm-border);
  border-radius: 8px; background: var(--lm-surface); box-shadow: var(--lm-shadow);
  font-size: var(--lm-small); line-height: 1.5; color: var(--lm-ink);
}
.lm-kpi {
  background: var(--lm-surface);
  border: 1px solid var(--lm-border);
  border-radius: 12px;
  box-shadow: var(--lm-shadow);
  padding: 16px;
  min-height: 108px;
  height: 100%;
}
.lm-kpi .lm-kpi-label {
  color: var(--lm-muted);
  font-size: var(--lm-small);
  font-weight: 500;
  margin: 0 0 8px;
}
.lm-kpi .lm-kpi-value {
  color: var(--lm-navy);
  font-size: clamp(1.5rem, 2vw, 1.75rem);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
  margin: 0;
}
.lm-concept-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin: 0.4rem 0 1.25rem;
  align-items: stretch;
}
.lm-concept-grid .lm-card {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}
.lm-concept-grid .lm-card p { flex: 1; }
.lm-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin: 0.35rem 0 0.75rem;
}
.lm-proof-kicker {
  margin: 1rem 0 0.4rem;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--lm-navy);
  opacity: 0.78;
}
.lm-method {
  max-width: none;
}
.lm-method p, .lm-method li {
  font-size: 15px;
  line-height: 1.6;
  color: var(--lm-ink);
}
.stApp:has(.lm-method-flag) .block-container .stMarkdown p,
.stApp:has(.lm-method-flag) .block-container [data-testid="stCaptionContainer"],
.stApp:has(.lm-method-flag) .block-container [data-testid="stExpander"] {
  max-width: none;
}
.stApp:has(.lm-method-flag) .lm-cons-grid,
.stApp:has(.lm-method-flag) .lm-cvrp-panel {
  max-width: none;
  margin-left: 0;
  margin-right: auto;
}
.stApp:has(.lm-method-flag) .lm-cvrp-panel { max-width: 800px; margin-inline: auto; }
.stApp:has(.lm-method-flag) .lm-section {
  margin-top: 1.15rem;
  margin-bottom: 0.35rem;
  padding-bottom: 0.28rem;
}
[data-testid="stElementContainer"]:has(.lm-method-flag) { display: none; }
[data-testid="stElementContainer"]:has(.lm-overview-flag) { display: none; }
.lm-cons-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
  margin: 0.5rem 0 1rem;
  align-items: stretch;
}
.lm-cons-grid .lm-card { min-height: 100%; }
.lm-cons-grid .lm-card:nth-child(-n+3) { grid-column: span 2; }
.lm-cons-grid .lm-card:nth-child(n+4) { grid-column: span 3; }
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
  font-size: 0.8125rem;
  border-top: 1px solid var(--lm-border);
  padding-top: 0.8rem;
  text-align: center;
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
  min-width: 640px;
  border-collapse: collapse;
  color: var(--lm-ink);
  font-size: var(--lm-small);
  line-height: 1.45;
}
.lm-table th, .lm-table td {
  padding: 0.52rem 0.65rem;
  border-right: 0;
  border-bottom: 1px solid #E4EAF0;
  text-align: left;
  vertical-align: top;
  white-space: normal;
}
.lm-table thead th {
  background: #EAF0F4;
  color: #111827;
  font-weight: 700;
  font-size: var(--lm-small);
  white-space: normal;
}
.lm-table tbody th {
  color: #111827;
  font-weight: 650;
  background: #F8FAFC;
}
.lm-table .lm-num {
  text-align: right;
  white-space: nowrap;
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
[data-testid="stMetricLabel"] {
  color: var(--lm-muted); height: auto; min-height: 2.8em; align-items: flex-start;
}
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] [data-testid="stMarkdownContainer"] {
  overflow: visible; white-space: normal;
}
[data-testid="stMetric"] { height: 100%; }
[data-testid="stNumberInput"] [data-testid="stWidgetLabel"] {
  min-height: 2.8em; align-items: flex-start;
}
[data-testid="stMetricLabel"] p {
  white-space: normal; overflow: visible; text-overflow: clip;
  font-size: var(--lm-small); line-height: 1.4;
}
div[data-testid="stMetricValue"] {
  font-size: 24px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
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
  min-height: 44px;
  padding: 0.46rem 0.95rem !important;
  border: 1px solid var(--lm-navy) !important;
  transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button:not(:disabled):hover, .stDownloadButton > button:not(:disabled):hover {
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
.stButton > button:disabled, .stDownloadButton > button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  box-shadow: none;
}
.stButton > button[kind="primary"]:not(:disabled):hover { background: var(--lm-navy-2) !important; }
[data-testid="stSidebarNavLink"] { transition: background-color 150ms ease; }
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
button:focus-visible, a:focus-visible, input:focus-visible, summary:focus-visible,
[role="radio"]:focus-visible {
  outline: 3px solid rgba(37, 99, 235, 0.45) !important;
  outline-offset: 2px !important;
}
[data-testid="stCaptionContainer"] { font-size: 13px; color: var(--lm-muted); }
div[data-testid="stStatusWidget"],
[data-testid="stStatus"] {
  min-height: 148px;
}
div[data-testid="stDataFrame"] {
  border: 1px solid var(--lm-border);
  border-radius: 9px;
  overflow: hidden;
  background: var(--lm-surface);
}
div[data-testid="stDataFrame"] [data-testid="stDataFrameResizable"] td {
  font-variant-numeric: tabular-nums;
}
@media (max-width: 760px) {
  .lm-hero { display: block; padding: 20px; min-height: auto; }
  .lm-hero-heading { margin-bottom: 16px; }
  .lm-hero .lm-kicker { padding-right: 60px; min-height: 48px; }
  .lm-route-motif { position: absolute; top: 20px; right: 20px; height: 48px; }
  .lm-route-motif svg.lm-hero-mark { width: 48px; height: 48px; }
  .lm-vehicle-grid { grid-template-columns: 1fr; }
  .lm-vehicle-grid .lm-route-cell { grid-column: 1; }
  .lm-lang-wrap { margin-bottom: 0.4rem; }
}
.lm-inner h1 { font-size: 28px; font-weight: 700; margin-bottom: 0.35rem; color: var(--lm-ink); }
@media (max-width: 760px) { .lm-inner h1 { font-size: 26px; } }
@media (min-width: 761px) { .lm-concept-grid .lm-card-heading { min-height: 47px; } }
.lm-inner p { color: var(--lm-muted); margin-bottom: 0.85rem; font-size: 16px; line-height: 1.55; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
  font-size: var(--lm-small) !important; color: var(--lm-muted); line-height: 1.5;
}

.stMarkdown .lm-hero p,
.stMarkdown .lm-inner p { max-width: none; }
.lm-table-wrap { max-height: 480px; }
.lm-table thead { position: sticky; top: 0; }
.lm-inner p { margin-bottom: .5rem; }
.st-key-plan-pair [data-testid="stHorizontalBlock"] {
  flex-wrap: nowrap;
  align-items: stretch;
}
.st-key-plan-pair [data-testid="stColumn"] {
  min-width: 0 !important;
}
.st-key-plan-pair .js-plotly-plot,
.st-key-plan-pair .plot-container {
  max-width: 100%;
}
@media (max-width: 1220px) {
  .st-key-plan-pair [data-testid="stHorizontalBlock"] {
    flex-direction: column;
    flex-wrap: wrap;
  }
  .st-key-plan-pair [data-testid="stColumn"] { width: 100% !important; flex: 1 1 100% !important; }
}
@media (max-width: 1100px) {
  .lm-concept-grid, .lm-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
  .block-container, [data-testid="stMainBlockContainer"] {
    padding-left: 16px !important; padding-right: 16px !important;
  }
  .lm-concept-grid, .lm-cons-grid { grid-template-columns: 1fr; }
  .lm-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .lm-cons-grid .lm-card:nth-child(-n+3),
  .lm-cons-grid .lm-card:nth-child(n+4) { grid-column: span 1; }
}

@media (max-width: 420px) {
  .lm-kpi-grid { grid-template-columns: 1fr; }
}

.lm-cvrp-panel {
  container-type: inline-size;
  text-align: center;
  margin: 8px 0 1.5rem;
}
.lm-cvrp-compare {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  width: 100%;
  margin: 0 0 0.5rem;
}
@container (max-width: 620px) {
  .lm-cvrp-compare { grid-template-columns: 1fr; }
}
.lm-cvrp-pane {
  display: flex;
  flex-direction: column;
  background: var(--lm-surface);
  border: 1px solid var(--lm-border);
  border-radius: 12px;
  padding: 4px 8px 12px;
  min-width: 0;
}
.stMarkdown .lm-cvrp-pane-title {
  margin: 8px 0 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--lm-navy);
  text-align: center;
}
.stMarkdown .lm-cvrp-pane-km {
  margin: 2px 0 2px;
  font-size: 14px;
  color: var(--lm-muted);
  text-align: center;
}
.lm-cvrp-pane .lm-cvrp {
  width: 100%;
  height: clamp(190px, 18vw, 250px);
  display: block;
}
@media (max-width: 760px) {
  .lm-cvrp-pane .lm-cvrp { height: auto; max-height: 250px; }
}
.lm-cvrp-panel .lm-assign {
  width: 100%;
  max-width: 720px;
  height: auto;
  display: block;
  margin: 0 auto;
}
.lm-cvrp-panel .lm-cvrp-cap {
  margin: 0.5rem auto 0;
  max-width: 72ch;
  text-align: center;
  color: var(--lm-muted);
  font-size: 14px;
  line-height: 1.45;
}
.st-key-scenario_presets [role="radiogroup"] {
  display: flex !important;
  flex-direction: column !important;
  gap: 10px !important;
}
.st-key-scenario_presets [data-baseweb="radio"] {
  display: flex !important;
  align-items: flex-start !important;
  gap: 10px;
  width: 100%;
  box-sizing: border-box;
  margin: 0 !important;
  padding: 14px 16px !important;
  border: 1px solid var(--lm-border);
  border-radius: 10px;
  background: var(--lm-surface);
  box-shadow: none !important;
}
.st-key-scenario_presets [data-baseweb="radio"] > div:last-child {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.st-key-scenario_presets [data-baseweb="radio"]:has(input:checked) {
  border-color: var(--lm-teal);
  background: rgba(15, 118, 110, 0.07);
}
.stApp:has(.lm-custom-open) .st-key-scenario_presets [data-baseweb="radio"]:has(input:checked) {
  border-color: var(--lm-border);
  background: var(--lm-surface);
}
.st-key-scenario_presets [data-baseweb="radio"] [data-testid="stMarkdownContainer"] p {
  margin: 0 !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  color: var(--lm-navy) !important;
  line-height: 1.3 !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  opacity: 1 !important;
}
.st-key-scenario_presets [role="radiogroup"] [data-testid="stCaptionContainer"] p {
  margin: 4px 0 0 !important;
  color: var(--lm-ink) !important;
  line-height: 1.4 !important;
  opacity: 1 !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  font-weight: 400 !important;
  font-size: 14px !important;
}
.st-key-scenario_presets [role="radiogroup"] [data-testid="stCaptionContainer"] p:first-child {
  font-size: 13px !important;
  font-weight: 500 !important;
}
.lm-custom-secondary {
  margin: 8px 0 0;
  padding: 12px 16px 14px;
  border: 1px dashed var(--lm-border);
  border-radius: 10px;
  background: var(--lm-surface-soft);
}
.lm-custom-secondary h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--lm-navy);
}
.lm-custom-secondary p {
  margin: 4px 0 0;
  font-size: 13px;
  line-height: 1.4;
  color: var(--lm-ink);
  max-width: none;
}
.st-key-custom-configure { margin-top: 0; }
.st-key-demand-editor,
.st-key-demand-preview {
  max-width: 580px;
}
.st-key-demand-editor [data-testid="stDataFrame"],
.st-key-demand-preview [data-testid="stDataFrame"] {
  font-size: 13.5px;
}
.st-key-demand-editor [data-testid="stDataFrame"] thead th,
.st-key-demand-preview [data-testid="stDataFrame"] thead th {
  font-size: 13px !important;
  font-weight: 600 !important;
}
.st-key-demand-editor [data-testid="stDataFrame"] td:last-child,
.st-key-demand-preview [data-testid="stDataFrame"] td:last-child {
  text-align: right !important;
  font-variant-numeric: tabular-nums;
}
.st-key-demand-editor [data-testid="stDataFrame"] th:last-child,
.st-key-demand-preview [data-testid="stDataFrame"] th:last-child {
  text-align: right !important;
}
.lm-custom-back { margin: 0 0 12px; }
.lm-feasibility {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin: 4px 0 10px;
}
.lm-feas-card {
  margin: 0;
  padding: 12px 14px;
  border: 1px solid var(--lm-border);
  border-radius: 10px;
  background: var(--lm-surface);
}
.lm-feas-card.is-pass {
  border-color: #9AD4C2;
  background: rgba(8, 122, 90, 0.06);
}
.lm-feas-card.is-fail {
  border-color: #E7B4AE;
  background: rgba(180, 35, 24, 0.06);
}
.lm-feas-card.is-info {
  background: var(--lm-surface-soft);
}
.lm-feas-title {
  margin: 0;
  font-size: 15px !important;
  font-weight: 650;
  color: var(--lm-navy) !important;
  line-height: 1.3;
}
.lm-feas-status {
  margin: 4px 0 0;
  font-size: 12.5px !important;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  line-height: 1.2;
}
.lm-feas-card.is-pass .lm-feas-status { color: var(--lm-success) !important; }
.lm-feas-card.is-fail .lm-feas-status { color: var(--lm-danger) !important; }
.lm-feas-card p {
  margin: 4px 0 0;
  font-size: 13.5px !important;
  line-height: 1.4;
  color: var(--lm-ink) !important;
  max-width: none;
}
.lm-feas-bar {
  height: 6px;
  margin: 8px 0 0;
  border-radius: 99px;
  background: #E6EEF2;
  overflow: hidden;
}
.lm-feas-bar > span {
  display: block;
  height: 100%;
  border-radius: 99px;
  background: var(--lm-teal);
}
.lm-feas-card.is-fail .lm-feas-bar > span { background: var(--lm-danger); }
.lm-order-flags {
  margin: 0 0 10px;
  padding: 8px 10px;
  border-left: 3px solid var(--lm-danger);
  background: rgba(180, 35, 24, 0.05);
}
.lm-order-flags p {
  margin: 0;
  font-size: 13px !important;
  line-height: 1.4;
  color: var(--lm-danger) !important;
  max-width: none;
}
.lm-order-flags p + p { margin-top: 4px; }
.lm-stale, .lm-ready {
  margin: 10px 0 0;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid var(--lm-border);
}
.lm-stale {
  border-left: 3px solid var(--lm-warning);
  background: #FFF8EE;
}
.lm-ready {
  border-left: 3px solid var(--lm-success);
  background: rgba(8, 122, 90, 0.06);
}
.lm-stale p, .lm-ready p {
  margin: 0;
  font-size: 13.5px !important;
  line-height: 1.4;
  color: var(--lm-ink) !important;
  max-width: none;
}
.lm-stale .lm-stale-title, .lm-ready .lm-ready-title {
  font-weight: 700;
  color: var(--lm-navy) !important;
}
.lm-packing {
  margin: 0 0 12px;
  font-size: 13.5px !important;
  line-height: 1.45;
  color: var(--lm-ink) !important;
  max-width: none;
}
@media (min-width: 1200px) {
  .stApp:has(.lm-custom-open) .st-key-scenario-preview {
    position: sticky;
    top: 12px;
  }
}
.stApp:has(.lm-custom-open) .st-key-scenario-presets-block { display: none; }
.stApp:has(.lm-custom-open) .lm-custom-secondary { display: none; }
@media (max-width: 900px) {
  .lm-feasibility { grid-template-columns: 1fr; }
}
.lm-preview-surface {
  border: 1px solid var(--lm-border);
  border-radius: 10px;
  background: var(--lm-surface);
}
.st-key-scenario-map {
  border: 1px solid var(--lm-border);
  border-radius: 10px;
  background: var(--lm-surface);
  min-height: 400px;
}
.lm-preview-empty {
  min-height: 220px;
  display: flex;
  align-items: center;
  padding: 20px 22px;
}
.lm-preview-empty p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: var(--lm-ink);
  max-width: 42ch;
}
.lm-preview-stats {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 6px 12px;
  margin: 12px 0 20px !important;
  text-align: center;
}
.lm-preview-stats div { min-width: 0; text-align: center; }
.stApp .lm-preview-stats dt {
  margin: 0 !important;
  font-size: 12.5px !important;
  font-weight: 600 !important;
  color: var(--lm-muted) !important;
  text-align: center !important;
  line-height: 1.3 !important;
}
.stApp .lm-preview-stats dd {
  margin: 6px 0 0 !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  color: var(--lm-navy) !important;
  font-variant-numeric: tabular-nums;
  text-align: center !important;
  line-height: 1.25 !important;
}
.lm-custom-configure-gap { height: 14px; }
.lm-offline {
  border: 1px solid var(--lm-border);
  border-left: 3px solid var(--lm-warning);
  border-radius: 8px;
  padding: 12px 14px;
  background: var(--lm-surface);
  margin: 0 0 12px;
}
.lm-offline-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--lm-navy);
}
.lm-offline-body {
  margin: 4px 0 0;
  font-size: 13px;
  line-height: 1.45;
  color: var(--lm-ink);
  max-width: none;
}
.stApp:has(.lm-scenarios-flag) .lm-inner { margin-bottom: 24px; }
.stApp:has(.lm-scenarios-flag) .lm-inner h1 { font-size: 28px; font-weight: 700; }
.stApp:has(.lm-scenarios-flag) .lm-inner p {
  font-size: 15px; line-height: 1.5; color: var(--lm-muted); margin-bottom: 0;
}
.stApp:has(.lm-scenarios-flag) .lm-section {
  margin: 0 0 16px; padding-bottom: 0; border-bottom: none;
}
.stApp:has(.lm-scenarios-flag) .lm-section h2 {
  font-size: 19px; font-weight: 600;
}
.st-key-scenario-action { margin-top: 24px; }
.st-key-scenario-action [data-testid="stHorizontalBlock"] { align-items: end; }
.stApp:has(.lm-scenarios-flag) .st-key-scenario-action [data-testid="stWidgetLabel"] p {
  font-size: 14px !important;
  font-weight: 600 !important;
  color: var(--lm-navy) !important;
}
.stApp:has(.lm-scenarios-flag) .stButton button {
  font-size: 15px !important;
  font-weight: 600 !important;
}
[data-testid="stMarkdownContainer"]:has(.lm-scenarios-flag),
[data-testid="stMarkdownContainer"]:has(.lm-custom-open),
[data-testid="stMarkdownContainer"]:has(.lm-plan-flag) { display: none; }
.stApp:has(.lm-plan-flag) .lm-section h2 {
  font-size: 19px;
  font-weight: 600;
}
.lm-plan-heading {
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin: 1.15rem 0 0.4rem;
}
.lm-plan-heading h2, .lm-plan-heading h3 {
  margin: 0;
  color: var(--lm-navy);
  font-weight: 600;
  line-height: 1.3;
}
.lm-plan-heading h2 { font-size: 19px; }
.lm-plan-heading h3 { font-size: 17px; }
.lm-plan-heading .lm-info-text {
  position: absolute; top: calc(100% + 8px); left: 0; right: auto; z-index: 10;
  width: min(420px, 100%);
  padding: 12px; margin: 0; border: 1px solid var(--lm-border);
  border-radius: 8px; background: var(--lm-surface); box-shadow: var(--lm-shadow);
  font-size: 13px; line-height: 1.45; color: var(--lm-ink); font-weight: 400;
}
.lm-plan-status {
  margin: 0 0 2px;
  font-size: 14px;
  font-weight: 600;
  color: var(--lm-success);
}
.lm-plan-status-text {
  margin: 0 0 8px;
  font-size: 13.5px;
  line-height: 1.45;
  color: var(--lm-muted);
}
.lm-plan-seq {
  margin: 0 0 10px;
  font-size: 14px;
  line-height: 1.5;
  overflow-wrap: anywhere;
}
.lm-plan-seq:last-child { margin-bottom: 0; }
.lm-plan-matrix {
  width: 100%;
  border-collapse: collapse;
  margin: 0.35rem 0 0.85rem;
  background: var(--lm-surface);
  border: 1px solid var(--lm-border);
  border-radius: 10px;
  overflow: hidden;
}
.lm-plan-matrix th, .lm-plan-matrix td {
  padding: 10px 12px;
  font-size: 14.5px;
  line-height: 1.4;
  border-bottom: 1px solid var(--lm-border);
  text-align: left;
}
.lm-plan-matrix thead th {
  font-size: 13px;
  font-weight: 600;
  color: var(--lm-navy);
  background: var(--lm-surface-soft);
}
.lm-plan-matrix tbody th { font-weight: 500; color: var(--lm-ink); }
.lm-plan-matrix td {
  text-align: center;
  font-weight: 600;
  color: var(--lm-success);
  width: 22%;
}
.lm-plan-matrix tr:last-child th, .lm-plan-matrix tr:last-child td { border-bottom: 0; }
.stApp:has(.lm-plan-flag) .lm-kpi-grid .lm-kpi:nth-child(3) {
  border-color: color-mix(in srgb, var(--lm-navy) 28%, var(--lm-border));
  box-shadow: 0 2px 10px rgba(23, 59, 87, 0.08);
}
.stApp:has(.lm-plan-flag) .st-key-plan_view [data-testid="stButtonGroup"],
.stApp:has(.lm-plan-flag) .st-key-plan_view .stButtonGroup {
  flex-wrap: wrap;
  gap: 6px;
  max-width: 100%;
}
.stApp:has(.lm-plan-flag) .st-key-plan_view button {
  min-height: 36px !important;
  height: auto !important;
  padding: 7px 14px !important;
  border-radius: 8px !important;
  border: 1px solid var(--lm-border) !important;
  background: var(--lm-surface) !important;
  color: var(--lm-navy) !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  white-space: nowrap;
}
.stApp:has(.lm-plan-flag) .st-key-plan_view button[aria-checked="true"],
.stApp:has(.lm-plan-flag) .st-key-plan_view button[aria-pressed="true"],
.stApp:has(.lm-plan-flag) .st-key-plan_view button[kind="primary"],
.stApp:has(.lm-plan-flag) .st-key-plan_view button[kind="segmented_controlActive"],
.stApp:has(.lm-plan-flag) .st-key-plan_view [data-testid="stBaseButton-segmented_controlActive"] {
  background: var(--lm-navy) !important;
  color: #FFFFFF !important;
  border-color: var(--lm-navy) !important;
}
.stApp:has(.lm-plan-flag) .st-key-plan_view
  [data-testid="stBaseButton-segmented_controlActive"] p,
.stApp:has(.lm-plan-flag) .st-key-plan_view
  [data-testid="stBaseButton-segmented_controlActive"] span,
.stApp:has(.lm-plan-flag) .st-key-plan_view button[kind="segmented_controlActive"] p,
.stApp:has(.lm-plan-flag) .st-key-plan_view button[kind="segmented_controlActive"] span {
  color: #FFFFFF !important;
}
@media (max-width: 760px) {
  .stApp:has(.lm-plan-flag) .st-key-plan_view button {
    white-space: normal;
    text-align: center;
  }
}
.lm-plan-checks {
  margin: 0 0 12px;
  padding: 0;
  list-style: none;
}
.lm-plan-checks li {
  margin: 0 0 6px;
  font-size: 14.5px !important;
  line-height: 1.45;
  color: var(--lm-ink) !important;
}
.lm-plan-checks li:last-child { margin-bottom: 0; }
.stApp:has(.lm-plan-flag) .stAlert p,
.stApp:has(.lm-plan-flag) [data-testid="stCaption"] {
  font-size: 13.5px !important;
}
.stApp:has(.lm-plan-flag) .st-key-plan-inspect button,
.stApp:has(.lm-plan-flag) .st-key-plan-review-inspect button,
.stApp:has(.lm-plan-flag) .st-key-plan-review-method button,
.stApp:has(.lm-plan-flag) .st-key-plan-inspect-baseline button,
.stApp:has(.lm-plan-flag) .st-key-plan-inspect-optimised button {
  min-height: 42px !important;
  height: 42px !important;
  padding: 0 18px !important;
  border-radius: 8px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  width: 100% !important;
}
.stApp:has(.lm-plan-flag) .st-key-plan-exports,
.stApp:has(.lm-plan-flag) .st-key-plan-review {
  margin-top: 1.15rem;
  margin-bottom: 0.35rem;
}
.stApp:has(.lm-plan-flag) .st-key-plan-pair .lm-table {
  min-width: 0;
}
.stApp:has(.lm-plan-flag) .st-key-plan-route-details [data-testid="stExpander"] {
  margin-bottom: 0.45rem;
}
@media (max-width: 1100px) {
  .lm-preview-stats { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
.lm-check { margin: 0.15rem 0 0.2rem; }
.stMarkdown .lm-check-title,
.lm-check-title {
  margin: 0;
  font-size: 16px !important;
  font-weight: 650;
  color: var(--lm-navy) !important;
  line-height: 1.3;
}
.stMarkdown .lm-check-detail,
.lm-check-detail {
  margin: 2px 0 0;
  font-size: 14px !important;
  color: var(--lm-ink) !important;
  line-height: 1.35;
}
.stMarkdown .lm-check-value,
.lm-check-value {
  margin: 4px 0 6px;
  font-size: 18px !important;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--lm-navy) !important;
  line-height: 1.2;
}
.lm-figure-title { color: var(--lm-navy); font-size: 16px; font-weight: 600; }

/* Keep the route structure readable while a highlight travels continuously. */
.lm-cvrp-pane .lm-cvrp-route-tracks path,
.lm-cvrp-pane .lm-cvrp-routes path {
  fill: none; stroke-width: 2.8; stroke-linejoin: round; stroke-linecap: round;
}
.lm-cvrp-route-tracks { opacity: 0.45; }
.lm-cvrp-pane .lm-cvrp-routes path {
  stroke-dasharray: 18 82;
  animation: lm-pane-route 5s linear infinite;
}
.lm-cvrp-pane .lm-cvrp-routes path:nth-child(2) { animation-delay: -1.25s; }
.lm-cvrp-pane .lm-cvrp-routes path:nth-child(3) { animation-delay: -2.5s; }
.lm-cvrp-pane .lm-cvrp-routes path:nth-child(4) { animation-delay: -3.75s; }
.lm-cvrp-pane .lm-cvrp-nodes .lm-cvrp-cust {
  fill: #F8FAFC;
  stroke: #94A3B8;
  stroke-width: 1.55;
  animation-duration: 5s;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}
.lm-cvrp-pane .lm-cvrp-nodes .lm-cvrp-r1 { --lm-visit: #2563EB; }
.lm-cvrp-pane .lm-cvrp-nodes .lm-cvrp-r2 { --lm-visit: #EA580C; animation-delay: -1.25s; }
.lm-cvrp-pane .lm-cvrp-nodes .lm-cvrp-r3 { --lm-visit: #7C3AED; animation-delay: -2.5s; }
.lm-cvrp-pane .lm-cvrp-nodes .lm-cvrp-r4 { --lm-visit: #C026D3; animation-delay: -3.75s; }
.lm-cvrp-pane .lm-cvrp-stops {
  paint-order: stroke;
  stroke: rgba(23, 59, 87, 0.42);
  stroke-width: 2.6px;
}
.lm-cvrp-pane .lm-cvrp-ids {
  fill: #586879; font-size: 16px; font-weight: 600;
  paint-order: stroke; stroke: white; stroke-width: 3px; pointer-events: none;
}
@keyframes lm-pane-route {
  from { stroke-dashoffset: 100; }
  to { stroke-dashoffset: 0; }
}
.lm-motion-tools { display: flex; justify-content: flex-end; margin-top: 6px; }
.lm-motion-control {
  display: inline-flex; align-items: center; gap: 7px; min-height: 32px;
  font-size: 14px; color: var(--lm-muted); cursor: pointer;
}
.lm-motion-control input { accent-color: var(--lm-teal); width: 16px; height: 16px; }
.stApp:has(.lm-motion-control input:checked) :is(.lm-hero, .lm-cvrp-panel) * {
  animation-play-state: paused !important;
}
.lm-assign-sheet, .lm-assign-sheet-label {
  opacity: 0; animation: lm-assign-sheet 10s ease-in-out infinite;
}
.lm-assign-orders { opacity: 0; animation: lm-assign-orders 10s ease-in-out infinite; }
.lm-assign-bars { opacity: 0; animation: lm-assign-bars 10s ease-in-out infinite; }
.lm-assign-fill {
  transform-box: fill-box; transform-origin: left center; transform: scaleX(0);
  animation: lm-assign-fill 10s ease-in-out infinite;
}
.lm-assign-routes path {
  fill: none; stroke-width: 2.8; stroke-linejoin: round; stroke-linecap: round;
  stroke-dasharray: 420; stroke-dashoffset: 420; opacity: 0;
  animation: lm-assign-route 10s ease-in-out infinite;
}
.lm-assign-routes path:nth-child(2) { animation-delay: 0.18s; }
.lm-assign-routes path:nth-child(3) { animation-delay: 0.32s; }
.lm-assign-label { opacity: 0; animation: lm-assign-label 10s ease-in-out infinite; }
@keyframes lm-assign-sheet {
  0% { opacity: 0; } 6% { opacity: 0.85; } 16% { opacity: 0.85; }
  24% { opacity: 0; } 100% { opacity: 0; }
}
@keyframes lm-assign-orders {
  0%, 14% { opacity: 0; } 22% { opacity: 1; } 48% { opacity: 0.28; }
  88% { opacity: 0.28; } 100% { opacity: 0; }
}
@keyframes lm-assign-bars {
  0%, 22% { opacity: 0; } 30% { opacity: 1; } 88% { opacity: 1; } 100% { opacity: 0; }
}
@keyframes lm-assign-fill {
  0%, 28% { transform: scaleX(0); }
  44% { transform: scaleX(1); }
  92% { transform: scaleX(1); }
  100% { transform: scaleX(1); }
}
@keyframes lm-assign-route {
  0%, 48% { stroke-dashoffset: 420; opacity: 0; }
  68% { stroke-dashoffset: 0; opacity: 1; }
  92% { stroke-dashoffset: 0; opacity: 1; }
  100% { stroke-dashoffset: 0; opacity: 1; }
}
@keyframes lm-assign-label {
  0%, 52% { opacity: 0; } 60%, 88% { opacity: 1; } 100% { opacity: 0; }
}
.lm-search-pulse {
  width: 72px; height: 48px; margin: 0.35rem 0 0.5rem;
}
.lm-search-pulse .lm-pulse-node {
  animation: lm-pulse 1.4s ease-in-out infinite;
}
@keyframes lm-pulse {
  0%, 100% { opacity: 0.35; }
  50% { opacity: 1; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition: none !important; animation: none !important; }
  .lm-hero-depot, .lm-hero-node { opacity: 1 !important; }
  .lm-hero-route { stroke-dashoffset: 0 !important; opacity: 1 !important; }
  .lm-cvrp-depot, .lm-cvrp-nodes circle, .lm-cvrp-routes path,
  .lm-cvrp-stops, .lm-assign-routes path { opacity: 1 !important; }
  .lm-cvrp-ids { opacity: 1 !important; }
  .lm-motion-tools { display: none; }
  .lm-cvrp-routes path, .lm-hero-route { stroke-dasharray: none !important; }
  .lm-assign-sheet, .lm-assign-sheet-label { opacity: 0 !important; }
  .lm-cvrp-routes path, .lm-assign-routes path {
    stroke-dashoffset: 0 !important;
  }
  .lm-cvrp-pane .lm-cvrp-nodes .lm-cvrp-cust {
    fill: var(--lm-visit) !important;
    stroke: var(--lm-visit) !important;
    opacity: 1 !important;
  }
  .lm-assign-orders, .lm-assign-bars, .lm-assign-label { opacity: 1 !important; }
  .lm-assign-fill { transform: scaleX(1) !important; }
}
[data-testid="stSidebarCollapsedControl"] {
  top: 8px; left: 16px;
  background: var(--lm-canvas);
  border-radius: 8px;
}
[data-testid="stSidebarCollapsedControl"] > div { visibility: visible; opacity: 1; }
[data-testid="stSidebarCollapsedControl"] button { min-width: 40px; min-height: 40px; }
[data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="false"])
[data-testid="stMainBlockContainer"] { padding-top: 76px !important; }
/* Wrap long localized labels without changing the established navigation. */
.lm-card, .lm-kpi { min-width: 0; overflow-wrap: break-word; }
.lm-inner h1 { line-height: 1.2; letter-spacing: -0.02em; }
.lm-section h2 { line-height: 1.3; }
abbr.lm-tip {
  text-decoration: underline dotted;
  text-underline-offset: 2px;
  cursor: help;
}
.stApp:has(.lm-overview-flag) .lm-kicker {
  font-size: 15px;
  font-weight: 600;
}
.stApp:has(.lm-overview-flag) .lm-hero h1 {
  font-size: clamp(28px, 2.4vw, 34px);
  font-weight: 700;
  line-height: 1.17;
  letter-spacing: -0.03em;
}
.stApp:has(.lm-overview-flag) .lm-hero p:not(.lm-hero-author):not(.lm-hero-context) {
  font-size: 16px;
  font-weight: 400;
  line-height: 1.55;
}
.stApp:has(.lm-overview-flag) .lm-hero-author {
  font-size: 14px !important;
  font-weight: 400;
}
.stApp:has(.lm-overview-flag) .lm-concept-grid .lm-card h3 {
  font-size: 17px;
  font-weight: 600;
  line-height: 1.3;
}
.stApp:has(.lm-overview-flag) .lm-concept-grid .lm-card > p {
  font-size: 15px;
  font-weight: 400;
  line-height: 1.5;
}
.stApp:has(.lm-overview-flag) .lm-concept-grid .lm-card .lm-info-text {
  font-size: 13px;
  font-weight: 400;
  line-height: 1.45;
}
.stApp:has(.lm-overview-flag) .stMarkdown .lm-cvrp-pane-title {
  font-size: 17px;
  font-weight: 600;
}
.stApp:has(.lm-overview-flag) .stMarkdown .lm-cvrp-pane-km {
  font-size: 14px;
  font-weight: 500;
}
.stApp:has(.lm-overview-flag) .lm-cvrp-cap {
  font-size: 13px;
  line-height: 1.45;
}
.stApp:has(.lm-overview-flag) .lm-motion-control { font-size: 13px; }
.stApp:has(.lm-overview-flag) .lm-proof-kicker {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: var(--lm-navy);
  opacity: 1;
}
.stApp:has(.lm-overview-flag) .lm-kpi .lm-kpi-label {
  font-size: 13px;
  font-weight: 500;
}
.stApp:has(.lm-overview-flag) .lm-kpi .lm-kpi-value {
  font-size: 26px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.stApp:has(.lm-overview-flag) [data-testid="stCaptionContainer"],
.stApp:has(.lm-overview-flag) [data-testid="stCaptionContainer"] p {
  font-size: 13px !important;
  color: var(--lm-muted);
  line-height: 1.45 !important;
}
.stApp:has(.lm-overview-flag) .stButton button {
  font-size: 15px !important;
  font-weight: 600 !important;
}
.stApp:has(.lm-overview-flag) .lm-footer { font-size: 13px; }
.stApp:has(.lm-overview-flag) [data-testid="stMarkdownContainer"]:has(.lm-about),
.stApp:has(.lm-overview-flag) .stMarkdown:has(.lm-about) {
  max-width: none !important;
  width: 100%;
}
.stApp:has(.lm-overview-flag) .lm-about {
  width: 100%;
  max-width: none;
  margin: 2.75rem 0 0;
  padding: 1.85rem 0 0.2rem;
  border-top: 1px solid var(--lm-border);
  text-align: center;
  background: transparent;
  box-shadow: none;
}
.stApp:has(.lm-overview-flag) .lm-about-kicker {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--lm-muted);
  margin: 0 auto 0.85rem;
  text-align: center;
  max-width: none;
}
.stApp:has(.lm-overview-flag) .lm-about-body {
  font-size: 16px;
  font-weight: 400;
  line-height: 1.55;
  color: var(--lm-muted);
  margin: 0 auto;
  text-align: center;
  width: 88%;
  max-width: none;
  overflow-wrap: break-word;
}
.stApp:has(.lm-overview-flag) .stMarkdown .lm-about p,
.stApp:has(.lm-overview-flag) .stMarkdown .lm-about-body {
  max-width: none !important;
  width: 88%;
  margin-left: auto;
  margin-right: auto;
  text-align: center;
}
@media (max-width: 760px) {
  .stApp:has(.lm-overview-flag) .lm-about {
    margin-top: 2rem;
    padding-top: 1.4rem;
  }
  .stApp:has(.lm-overview-flag) .lm-about-body,
  .stApp:has(.lm-overview-flag) .stMarkdown .lm-about p,
  .stApp:has(.lm-overview-flag) .stMarkdown .lm-about-body {
    width: 100%;
  }
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
    sub = t("brand.sub").replace("\\", "\\\\").replace('"', '\\"')
    brand = f':root{{--lm-brand-sub:"{sub}";}}'
    st.markdown(
        THEME_CSS.replace("</style>", _vehicle_colour_css() + brand + "</style>"),
        unsafe_allow_html=True,
    )


BRAND_MARK_SVG = """
<svg viewBox="0 0 32 32" aria-hidden="true">
  <rect width="32" height="32" rx="7" fill="#102A3A"/>
  <path d="M16 16 L6.5 7 M16 16 L25.5 8 M16 16 L24.5 24.5"
    stroke="#99F6E4" stroke-width="2" stroke-linecap="round"/>
  <rect x="12" y="12" width="8" height="8" rx="1.5" fill="#4FD1C5"/>
  <circle cx="6.5" cy="7" r="2.6" fill="#2563EB"/>
  <circle cx="25.5" cy="8" r="2.6" fill="#EA580C"/>
  <circle cx="24.5" cy="24.5" r="2.6" fill="#7C3AED"/>
</svg>
"""

HERO_MARK_SVG = """
<svg class="lm-hero-mark" viewBox="0 0 32 32" aria-hidden="true">
  <rect width="32" height="32" rx="7" fill="#102A3A"/>
  <path class="lm-hero-route r1" d="M16 16 L6.5 7"/>
  <path class="lm-hero-route r2" d="M16 16 L25.5 8"/>
  <path class="lm-hero-route r3" d="M16 16 L24.5 24.5"/>
  <rect class="lm-hero-depot" x="12" y="12" width="8" height="8" rx="1.5" fill="#4FD1C5"/>
  <circle class="lm-hero-node n1" cx="6.5" cy="7" r="2.6" fill="#2563EB"/>
  <circle class="lm-hero-node n2" cx="25.5" cy="8" r="2.6" fill="#EA580C"/>
  <circle class="lm-hero-node n3" cx="24.5" cy="24.5" r="2.6" fill="#7C3AED"/>
</svg>
"""

INFO_ICON_SVG = """
<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">
  <circle cx="8" cy="8" r="6.25" fill="none" stroke="currentColor" stroke-width="1.35"/>
  <circle cx="8" cy="5.15" r="0.85" fill="currentColor"/>
  <path d="M8 7.2 v4.05" fill="none" stroke="currentColor"
    stroke-width="1.4" stroke-linecap="round"/>
</svg>
"""

SEARCH_PULSE_SVG = """
<div class="lm-search-pulse" aria-hidden="true">
  <svg viewBox="0 0 72 48">
    <rect x="32" y="20" width="8" height="8" rx="1" fill="#173B57" class="lm-pulse-node"/>
    <circle cx="12" cy="12" r="3.5" fill="#2563EB" class="lm-pulse-node"/>
    <circle cx="60" cy="14" r="3.5" fill="#EA580C" class="lm-pulse-node"/>
    <circle cx="58" cy="36" r="3.5" fill="#7C3AED" class="lm-pulse-node"/>
    <path d="M36 24 L12 12 M36 24 L60 14 M36 24 L58 36"
      fill="none" stroke="#0F766E" stroke-width="1.6"/>
  </svg>
</div>
"""


def boot_page() -> None:
    ensure_session()
    inject_theme()
    render_language_bar()


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


def render_brand() -> None:
    st.markdown(
        '<div class="lm-brand">'
        f'<div class="lm-mark">{BRAND_MARK_SVG}</div>'
        '<div><div class="lm-name">LastMile Lab</div>'
        f'<div class="lm-sub">{escape(t("brand.sub"))}</div></div></div>',
        unsafe_allow_html=True,
    )


def render_language_bar() -> None:
    ensure_session()
    with st.sidebar:
        st.markdown(
            f'<div class="lm-lang-label">{escape(t("nav.language"))}</div>',
            unsafe_allow_html=True,
        )
        st.radio(
            t("lang.label"),
            ["en", "de"],
            format_func=lambda code: "English" if code == "en" else "Deutsch",
            key="ui_language",
            horizontal=True,
            label_visibility="collapsed",
        )
        _render_service_status()


def _render_service_status() -> None:
    import httpx

    from api_client import backend_url

    try:
        response = httpx.get(f"{backend_url()}/health", timeout=0.6)
        label = t("api.status.on") if response.is_success else t("api.status.off")
    except Exception:
        label = t("api.status.off")
    st.markdown(f'<div class="lm-api-status">{escape(label)}</div>', unsafe_allow_html=True)


def page_header(
    title: str,
    subtitle: str,
    *,
    kicker: str | None = None,
    extra: str | list[str] | None = None,
    context: str | None = None,
    author: str | None = None,
    compact: bool = True,
) -> None:
    if compact:
        st.markdown(
            f'<div class="lm-inner"><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>',
            unsafe_allow_html=True,
        )
        return
    kicker_html = f'<div class="lm-kicker">{escape(kicker)}</div>' if kicker else ""
    extras = extra if isinstance(extra, list) else ([extra] if extra else [])
    copy_parts = [f"<p>{escape(subtitle)}</p>"]
    copy_parts.extend(f"<p>{escape(block)}</p>" for block in extras)
    if context:
        copy_parts.append(f'<p class="lm-hero-context">{escape(context)}</p>')
    if author:
        copy_parts.append(f'<p class="lm-hero-author">{escape(author)}</p>')
    # Streamlit markdown treats a blank line as the end of an HTML block, so
    # omitted optional paragraphs must not leave empty lines in the template.
    copy_html = "".join(copy_parts)
    st.markdown(
        (
            f'<div class="lm-hero"><div class="lm-hero-heading">{kicker_html}'
            f"<h1>{escape(title)}</h1></div>"
            f'<div class="lm-route-motif" aria-hidden="true">{HERO_MARK_SVG}</div>'
            f'<div class="lm-hero-copy">{copy_html}</div></div>'
        ),
        unsafe_allow_html=True,
    )


def section(title: str, caption: str | None = None) -> None:
    caption_html = f"<p>{escape(caption)}</p>" if caption else ""
    st.markdown(
        f'<div class="lm-section"><h2>{escape(title)}</h2>{caption_html}</div>',
        unsafe_allow_html=True,
    )


def heading_with_tip(title: str, tip: str, *, level: str = "h2") -> None:
    heading = "h3" if level == "h3" else "h2"
    st.markdown(
        f'<div class="lm-plan-heading"><{heading}>{escape(title)}</{heading}>'
        f'<details class="lm-info"><summary aria-label="{escape(title)}">'
        f'{INFO_ICON_SVG}</summary><p class="lm-info-text">{escape(tip)}</p></details></div>',
        unsafe_allow_html=True,
    )


def term(label: str, tip_key: str) -> str:
    return (
        f'<abbr class="lm-tip" title="{escape(t(tip_key))}">{escape(label)}</abbr>'
    )


def with_terms(markup: str, replacements: list[tuple[str, str]]) -> str:
    tokens: list[tuple[str, str]] = []
    for index, (phrase, tip_key) in enumerate(replacements):
        token = f"@@TERM{index}@@"
        if phrase in markup:
            markup = markup.replace(phrase, token, 1)
            tokens.append((token, term(phrase, tip_key)))
    for token, html in tokens:
        markup = markup.replace(token, html)
    return markup


def gloss_first_tote(markup: str) -> str:
    if "totes (" in markup:
        return markup.replace("totes", term("totes", "tip.tote"), 1)
    if "Totes (" in markup:
        return markup.replace("Totes", term("Totes", "tip.tote"), 1)
    return markup


def concept_cards(items: list[tuple[str, str, str]]) -> None:
    cards = "".join(
        '<article class="lm-card"><div class="lm-card-heading">'
        f"<h3>{escape(title)}</h3>"
        f'<details class="lm-info"><summary aria-label="{escape(title)}">'
        f'{INFO_ICON_SVG}</summary><p class="lm-info-text">{escape(tip)}</p></details></div>'
        f"<p>{escape(body)}</p></article>"
        for title, body, tip in items
    )
    st.markdown(
        f'<div class="lm-concept-grid" lang="{current_language()}">{cards}</div>',
        unsafe_allow_html=True,
    )


def kpi_cards(items: list[tuple[str, str]]) -> None:
    cards = "".join(
        f'<div class="lm-kpi"><p class="lm-kpi-label">{escape(label)}</p>'
        f'<p class="lm-kpi-value">{escape(value)}</p></div>'
        for label, value in items
    )
    st.markdown(f'<div class="lm-kpi-grid">{cards}</div>', unsafe_allow_html=True)


def constraint_cards(items: list[tuple[str, str]]) -> None:
    cards = "".join(
        f'<article class="lm-card"><h3>{escape(title)}</h3><p>{escape(body)}</p></article>'
        for title, body in items
    )
    st.markdown(f'<div class="lm-cons-grid">{cards}</div>', unsafe_allow_html=True)


_CVRP_DEPOT = (320, 185)
_CVRP_CUSTOMER_IDS: dict[tuple[int, int], str] = {
    (200, 70): "C1",
    (140, 95): "C2",
    (175, 145): "C3",
    (445, 65): "C4",
    (520, 100): "C5",
    (485, 155): "C6",
    (500, 250): "C7",
    (545, 285): "C8",
    (430, 295): "C9",
    (200, 265): "C10",
    (125, 245): "C11",
    (155, 305): "C12",
}
_CVRP_NN_ROUTES: list[tuple[str, list[tuple[int, int]]]] = [
    ("#2563EB", [(200, 70), (445, 65), (140, 95)]),
    ("#EA580C", [(520, 100), (175, 145), (500, 250)]),
    ("#7C3AED", [(485, 155), (125, 245), (545, 285)]),
    ("#C026D3", [(430, 295), (200, 265), (155, 305)]),
]
_CVRP_OPT_ROUTES: list[tuple[str, list[tuple[int, int]]]] = [
    ("#2563EB", [(200, 70), (140, 95), (175, 145)]),
    ("#EA580C", [(445, 65), (520, 100), (485, 155)]),
    ("#7C3AED", [(500, 250), (545, 285), (430, 295)]),
    ("#C026D3", [(200, 265), (125, 245), (155, 305)]),
]


def _cvrp_seg_len(start: tuple[int, int], end: tuple[int, int]) -> float:
    return ((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2) ** 0.5


def _cvrp_arrival_pcts(stops: list[tuple[int, int]]) -> list[float]:
    points = [_CVRP_DEPOT, *stops, _CVRP_DEPOT]
    lengths = [
        _cvrp_seg_len(points[index], points[index + 1])
        for index in range(len(points) - 1)
    ]
    total = sum(lengths) or 1.0
    cumulative = 0.0
    arrivals: list[float] = []
    for length in lengths[:-1]:
        cumulative += length
        arrivals.append(100.0 * cumulative / total)
    return arrivals


def _cvrp_visit_keyframes() -> str:
    idle_fill = "#F8FAFC"
    idle_stroke = "#94A3B8"
    chunks: list[str] = []
    for pane, routes in enumerate((_CVRP_NN_ROUTES, _CVRP_OPT_ROUTES)):
        for route_index, (_colour, stops) in enumerate(routes):
            for stop_index, percent in enumerate(_cvrp_arrival_pcts(stops)):
                name = f"lm-cvrp-arr-{pane}-{route_index}-{stop_index}"
                arrival = round(percent, 2)
                arrival_before = max(round(arrival - 0.01, 2), 0.0)
                pulse = min(round(arrival + 1.2, 2), 99.2)
                settled = min(round(arrival + 2.4, 2), 99.6)
                chunks.append(
                    f".{name}{{animation-name:{name};}}"
                    f"@keyframes {name}{{"
                    f"0%,{arrival_before:.2f}%{{fill:{idle_fill};stroke:{idle_stroke};opacity:1;}}"
                    f"{arrival:.2f}%{{fill:var(--lm-visit);stroke:var(--lm-visit);opacity:1;}}"
                    f"{pulse:.2f}%{{fill:var(--lm-visit);stroke:var(--lm-visit);opacity:.75;}}"
                    f"{settled:.2f}%,100%{{fill:var(--lm-visit);stroke:var(--lm-visit);opacity:1;}}"
                    f"}}"
                )
    return "".join(chunks)


THEME_CSS = THEME_CSS.replace("</style>", _cvrp_visit_keyframes() + "\n</style>", 1)


def _cvrp_route_path(depot: tuple[int, int], stops: list[tuple[int, int]]) -> str:
    dx, dy = depot
    parts = [f"M{dx} {dy}"]
    parts.extend(f"L{x} {y}" for x, y in stops)
    parts.append("Z")
    return " ".join(parts)


def _cvrp_id_label(point: tuple[int, int], customer_id: str) -> str:
    dx, dy = _CVRP_DEPOT
    x, y = point
    vx, vy = x - dx, y - dy
    length = max((vx * vx + vy * vy) ** 0.5, 1.0)
    tx = min(max(x + 23 * vx / length, 18), 622)
    ty = min(max(y + 19 * vy / length, 14), 328)
    if tx < x - 4:
        anchor = "end"
    elif tx > x + 4:
        anchor = "start"
    else:
        anchor = "middle"
    return (
        f'<text x="{tx:.0f}" y="{ty:.0f}" text-anchor="{anchor}">{escape(customer_id)}</text>'
    )


def _cvrp_pane_svg(
    title: str,
    subtitle: str,
    depot_label: str,
    routes: list[tuple[str, list[tuple[int, int]]]],
    aria: str,
    pane: int,
) -> str:
    dx, dy = _CVRP_DEPOT
    customers = [point for _, stops in routes for point in stops]
    nodes: list[str] = []
    marks: list[str] = []
    for route_index, (_colour, stops) in enumerate(routes):
        route_class = f"lm-cvrp-r{route_index + 1}"
        for stop_index, (x, y) in enumerate(stops):
            name = f"lm-cvrp-arr-{pane}-{route_index}-{stop_index}"
            nodes.append(
                f'<circle class="lm-cvrp-cust {route_class} {name}" '
                f'cx="{x}" cy="{y}" r="10.5"/>'
            )
            marks.append(f'<text x="{x}" y="{y + 4}">{stop_index + 1}</text>')
    paths = "".join(
        f'<path pathLength="100" stroke="{colour}" d="{_cvrp_route_path(_CVRP_DEPOT, stops)}"/>'
        for colour, stops in routes
    )
    ids = "".join(
        _cvrp_id_label(point, _CVRP_CUSTOMER_IDS[point])
        for point in customers
        if point in _CVRP_CUSTOMER_IDS
    )
    return (
        f'<article class="lm-cvrp-pane">'
        f'<svg class="lm-cvrp" viewBox="60 20 540 315" role="img" '
        f'aria-label="{escape(f"{title}. {aria}")}">'
        f'<g class="lm-cvrp-route-tracks" aria-hidden="true">{paths}</g>'
        f'<g class="lm-cvrp-routes" fill="none">{paths}</g>'
        f'<g class="lm-cvrp-nodes">{"".join(nodes)}</g>'
        f'<g class="lm-cvrp-ids">{ids}</g>'
        f'<g class="lm-cvrp-stops" font-size="14" font-weight="700" '
        f'text-anchor="middle" fill="#FFFFFF">{"".join(marks)}</g>'
        f'<g class="lm-cvrp-depot">'
        f'<rect x="{dx - 10}" y="{dy - 10}" width="20" height="20" rx="3" fill="#173B57"/>'
        f'<text x="{dx}" y="{dy + 28}" text-anchor="middle" fill="#173B57" '
        f'font-size="16">{escape(depot_label)}</text></g></svg>'
        f'<p class="lm-cvrp-pane-title">{escape(title)}</p>'
        f'<p class="lm-cvrp-pane-km">{escape(subtitle)}</p>'
        f'</article>'
    )


def animation_control_html() -> str:
    return (
        '<div class="lm-motion-tools"><label class="lm-motion-control">'
        f'<input type="checkbox">{escape(t("ux.motion.pause"))}</label></div>'
    )


def cvrp_animation_html(result_label: str, aria_label: str) -> str:
    optimized_km = result_label
    if "→" in result_label:
        optimized_km = result_label.split("→", 1)[1].strip()
    total = t("ux.over.anim.total")
    panes = _cvrp_pane_svg(
        t("ux.over.anim.baseline"),
        f"{total}: {t('ux.over.anim.km')}",
        t("ux.over.anim.depot"),
        _CVRP_NN_ROUTES,
        aria_label,
        0,
    ) + _cvrp_pane_svg(
        t("ux.over.anim.optimized"),
        f"{total}: {optimized_km}",
        t("ux.over.anim.depot"),
        _CVRP_OPT_ROUTES,
        aria_label,
        1,
    )
    return (
        f'<div class="lm-cvrp-panel"><div class="lm-cvrp-compare">{panes}</div>'
        f'<p class="lm-cvrp-cap">{escape(t("ux.over.diagram"))}</p>'
        f'{animation_control_html()}</div>'
    )


def methodology_animation_html() -> str:
    sheet = escape(t("ux.method.figure.sheet"))
    label = escape(t("ux.method.figure.label"))
    caption = escape(t("ux.method.figure.caption"))
    cells = []
    for row in range(4):
        for col in range(8):
            x = 184 + col * 34
            y = 40 + row * 20
            cells.append(f'<rect x="{x}" y="{y}" width="28" height="16" rx="2"/>')
    orders = (
        '<g transform="translate(56,78)">'
        '<circle cx="12" cy="8" r="6" fill="#64748B"/>'
        '<rect x="0" y="20" width="8" height="8" fill="#94A3B8"/>'
        '<rect x="9" y="20" width="8" height="8" fill="#94A3B8"/>'
        '<rect x="18" y="20" width="8" height="8" fill="#94A3B8"/></g>'
        '<g transform="translate(156,78)">'
        '<circle cx="12" cy="8" r="6" fill="#64748B"/>'
        '<rect x="4" y="20" width="8" height="8" fill="#94A3B8"/>'
        '<rect x="13" y="20" width="8" height="8" fill="#94A3B8"/></g>'
        '<g transform="translate(256,78)">'
        '<circle cx="12" cy="8" r="6" fill="#64748B"/>'
        '<rect x="-4" y="20" width="8" height="8" fill="#94A3B8"/>'
        '<rect x="5" y="20" width="8" height="8" fill="#94A3B8"/>'
        '<rect x="14" y="20" width="8" height="8" fill="#94A3B8"/>'
        '<rect x="23" y="20" width="8" height="8" fill="#94A3B8"/></g>'
        '<g transform="translate(356,78)">'
        '<circle cx="12" cy="8" r="6" fill="#64748B"/>'
        '<rect x="4" y="20" width="8" height="8" fill="#94A3B8"/>'
        '<rect x="13" y="20" width="8" height="8" fill="#94A3B8"/></g>'
        '<g transform="translate(456,78)">'
        '<circle cx="12" cy="8" r="6" fill="#64748B"/>'
        '<rect x="0" y="20" width="8" height="8" fill="#94A3B8"/>'
        '<rect x="9" y="20" width="8" height="8" fill="#94A3B8"/>'
        '<rect x="18" y="20" width="8" height="8" fill="#94A3B8"/></g>'
        '<g transform="translate(556,78)">'
        '<circle cx="12" cy="8" r="6" fill="#64748B"/>'
        '<rect x="4" y="20" width="8" height="8" fill="#94A3B8"/>'
        '<rect x="13" y="20" width="8" height="8" fill="#94A3B8"/></g>'
    )
    return f"""
    <div class="lm-cvrp-panel">
    <div class="lm-figure-title">{label}</div>
    <svg class="lm-assign" viewBox="0 0 640 320" role="img" aria-label="{label}">
      <g class="lm-assign-sheet" fill="#E2E8F0" stroke="#CBD5E1" stroke-width="1">
        {''.join(cells)}
      </g>
      <text class="lm-assign-sheet-label" x="320" y="28" text-anchor="middle"
        fill="#64748B" font-size="13">{sheet}</text>
      <g class="lm-assign-orders">{orders}</g>
      <g class="lm-assign-bars">
        <rect x="200" y="148" width="240" height="22" rx="4" fill="#F8FAFC" stroke="#94A3B8"/>
        <rect x="200" y="178" width="240" height="22" rx="4" fill="#F8FAFC" stroke="#94A3B8"/>
        <rect x="200" y="208" width="240" height="22" rx="4" fill="#F8FAFC" stroke="#94A3B8"/>
        <g class="lm-assign-fill">
          <rect x="202" y="150" width="148" height="18" rx="3" fill="#2563EB"/>
          <rect x="202" y="180" width="208" height="18" rx="3" fill="#EA580C"/>
          <rect x="202" y="210" width="118" height="18" rx="3" fill="#7C3AED"/>
        </g>
        <rect x="310" y="248" width="20" height="20" rx="3" fill="#173B57"/>
      </g>
      <g class="lm-assign-routes" fill="none">
        <path stroke="#2563EB" d="M320 258 L230 238 L190 268 Z"/>
        <path stroke="#EA580C" d="M320 258 L410 232 L470 262 Z"/>
        <path stroke="#7C3AED" d="M320 258 L300 292 L390 298 Z"/>
      </g>
    </svg>
    <p class="lm-cvrp-cap">{caption}</p>
    {animation_control_html()}
    </div>
    """


def html_write(markup: str) -> None:
    st.markdown(f"<p>{markup}</p>", unsafe_allow_html=True)


def search_pulse() -> None:
    st.markdown(SEARCH_PULSE_SVG, unsafe_allow_html=True)


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
                value is None or (isinstance(value, int | float) and not isinstance(value, bool))
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
            rendered = escape(display)
            if re.fullmatch(r"V\d{2}", display):
                rendered = (
                    f'<span style="border-left:4px solid {vehicle_colour(display)};'
                    f'padding-left:8px">{rendered}</span>'
                )
            css_class = "lm-num" if column in numeric else ""
            if column == row_header:
                cells.append(f'<th class="{css_class}" scope="row">{rendered}</th>')
            else:
                cells.append(f'<td class="{css_class}">{rendered}</td>')
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    html = (
        '<div class="lm-table-wrap" tabindex="0"><table class="lm-table">'
        f"<thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody></table></div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def empty_state(title: str, body: str) -> None:
    st.markdown(
        f'<div class="lm-empty"><strong>{title}</strong><br/>{body}</div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Dispatch_Setup.py", label=t("empty.open"))


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


def render_overview_about() -> None:
    st.markdown(
        (
            '<div class="lm-about">'
            f'<div class="lm-about-kicker">{escape(t("ux.over.about.kicker"))}</div>'
            f'<div class="lm-about-body">{escape(t("ux.over.about.body"))}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        f'<div class="lm-footer">{t("footer")}</div>',
        unsafe_allow_html=True,
    )


PLANNING_START_CMD = (
    r".\.venv\Scripts\python.exe -m uvicorn app.main:app "
    "--app-dir backend --host 127.0.0.1 --port 8000"
)


def planning_service_up() -> bool:
    import httpx

    from api_client import backend_url

    try:
        response = httpx.get(f"{backend_url()}/health", timeout=0.6)
        return response.is_success
    except Exception:
        return False


def planning_offline_notice() -> None:
    st.markdown(
        (
            f'<div class="lm-offline"><p class="lm-offline-title">'
            f'{escape(t("ux.api.offline.title"))}</p>'
            f'<p class="lm-offline-body">{escape(t("ux.api.offline.body"))}</p></div>'
        ),
        unsafe_allow_html=True,
    )
    with st.expander(t("ux.api.command"), expanded=False):
        st.code(PLANNING_START_CMD, language="powershell")


def call_api(func: Callable[..., Any], *args: Any, notify: bool = True, **kwargs: Any) -> Any:
    try:
        return func(*args, **kwargs)
    except ApiError as exc:
        if exc.kind == "connection":
            st.session_state["_planning_offline"] = True
            if notify:
                st.error(str(exc))
                st.caption("In PowerShell: " + PLANNING_START_CMD)
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


def export_buttons(run_id: str, *, visible: bool = False) -> None:
    from api_client import export_run

    with st.container() if visible else st.expander(t("export.title"), expanded=False):
        cache = st.session_state.setdefault("_export_payloads", {})
        if st.button(t("ux.export.prepare"), key=f"prepare-{run_id}"):
            for fmt in ("json", "csv"):
                payload = call_api(export_run, run_id, fmt)
                if payload is not None:
                    cache[(run_id, fmt)] = payload
        for column, fmt in zip(st.columns(2), ("json", "csv"), strict=True):
            if (run_id, fmt) in cache:
                content, mime, name = cache[(run_id, fmt)]
                column.download_button(
                    t(f"export.{fmt}"),
                    data=content,
                    file_name=name,
                    mime=mime,
                    key=f"export-{fmt}-{run_id}",
                    on_click="ignore",
                )


def status_badge(
    status: str | None,
    *,
    run_type: str | None = None,
    scenario_id: str | None = None,
) -> None:
    if not status:
        st.info(t("status.none"))
        return
    label_key = f"status.{status}.label"
    hint_key = f"status.{status}.hint"
    label = t(label_key)
    hint = t(hint_key)
    if status == "feasible":
        hint = t("ux.status.feasible")
        if run_type == "optimised":
            hint += " " + t("ux.status.search")
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
