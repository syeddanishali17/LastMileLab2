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
from i18n import t
from state import ensure_session

THEME_CSS = """
<style>

:root {
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
html, body, [class*="css"] {
  font-family: "Inter", "Segoe UI", system-ui, sans-serif;
}
[data-testid="stAppViewContainer"], .stApp { background: var(--lm-canvas); }
.block-container {
  padding-top: 1.4rem;
  padding-bottom: 2rem;
  padding-left: 1.85rem;
  padding-right: 1.85rem;
  max-width: 1300px;
}
[data-testid="stAppToolbar"],
.stAppToolbar {
  display: none !important;
}
#MainMenu, footer { visibility: hidden; }

[data-testid="stSidebar"] {
  background: var(--lm-sidebar);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}
section[data-testid="stSidebar"] > div:first-child {
  padding-top: 1.35rem;
  padding-bottom: 1rem;
}
[data-testid="stSidebar"] * { color: #F7FAFC !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255, 255, 255, 0.12); }
[data-testid="stSidebarNav"] { padding-top: 0.35rem; }
[data-testid="stSidebarNavItems"] { gap: 0.15rem; }
[data-testid="stSidebarNavLink"] {
  border-radius: 0 !important;
  border-left: 3px solid transparent !important;
  padding: 0.42rem 0.7rem !important;
  margin: 0.1rem 0 !important;
  font-size: 14px !important;
  font-weight: 400 !important;
  line-height: 1.35 !important;
}
[data-testid="stSidebarNavLink"]:hover {
  background: rgba(255, 255, 255, 0.06) !important;
}
[data-testid="stSidebarNavLink"] span {
  font-size: 14px !important;
}
[data-testid="stSidebarNavSeparator"],
[data-testid="stNavSectionHeader"],
[data-testid="stSidebarNav"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebarNav"] small,
[data-testid="stSidebarNav"] li div p {
  font-size: 10.5px !important;
  font-weight: 600 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  opacity: 0.72;
  margin-top: 1.15rem !important;
  margin-bottom: 0.35rem !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"],
[data-testid="stSidebarNav"] a[aria-current="page"] {
  background: #1B4059 !important;
  border-left: 3px solid #4FD1C5 !important;
  box-shadow: inset 3px 0 0 #4FD1C5;
  font-weight: 600 !important;
  color: #FFFFFF !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"]::after,
[data-testid="stSidebarNav"] a[aria-current="page"]::after,
[data-testid="stSidebarNavLink"][aria-current="page"]::before {
  content: none !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 9px;
}

.lm-brand {
  display: flex; gap: 0.7rem; align-items: center;
  margin: 0 0 0.35rem 0;
}
.lm-mark {
  width: 28px; height: 28px; flex: 0 0 28px;
}
.lm-mark svg { display: block; width: 28px; height: 28px; }
.lm-name { font-size: 17px; font-weight: 600; line-height: 1.15; color: #FFFFFF; }
.lm-sub { font-size: 12px; opacity: 0.78; margin-top: 0.12rem; font-weight: 400; }
.lm-lang-label {
  font-size: 10.5px; font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; opacity: 0.72; margin: 1.2rem 0 0.35rem;
}
.lm-api-status {
  font-size: 12px; opacity: 0.7; margin-top: 0.85rem;
}

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
  font-size: clamp(1.9rem, 3vw, 2.2rem);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.15;
  margin: 0 0 0.7rem 0;
  color: #FFFFFF;
  overflow-wrap: anywhere;
}
.lm-hero p {
  margin: 0 0 0.7rem 0;
  color: #D9E4EC;
  max-width: 46rem;
  line-height: 1.55;
  font-size: 15px;
  font-weight: 400;
}
.lm-hero p:last-child { margin-bottom: 0; }
.lm-hero-context {
  color: #B7C9D4 !important;
  font-size: 13px !important;
  margin-top: 0.35rem !important;
}
.lm-kicker {
  color: #99F6E4;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 0.65rem;
}
.lm-route-motif {
  position: relative; height: 116px; opacity: 0.9;
  display: flex; align-items: center; justify-content: center;
}
.lm-route-motif svg { width: 88px; height: 88px; }
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
.lm-card h3 { margin: 0 0 0.4rem; color: var(--lm-navy); font-size: 15px; font-weight: 600; }
.lm-card p {
  margin: 0; color: var(--lm-muted); font-size: 14px; line-height: 1.55; font-weight: 400;
}
.lm-concept-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin: 0.4rem 0 1.25rem;
  align-items: stretch;
}
.lm-concept-grid .lm-card { min-height: 100%; }
.lm-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin: 0.35rem 0 0.75rem;
}
.lm-kpi {
  background: var(--lm-surface);
  border: 1px solid var(--lm-border);
  border-radius: 12px;
  box-shadow: var(--lm-shadow);
  padding: 1rem 1.05rem;
  min-height: 102px;
}
.lm-kpi .lm-kpi-label {
  color: var(--lm-muted);
  font-size: 13px;
  font-weight: 500;
  margin: 0 0 0.4rem;
}
.lm-kpi .lm-kpi-value {
  color: var(--lm-navy);
  font-size: 24px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
  margin: 0;
}
.lm-method {
  max-width: 760px;
}
.lm-method p, .lm-method li {
  font-size: 15px;
  line-height: 1.6;
  color: var(--lm-ink);
}
.stApp:has(.lm-method-flag) .block-container .stMarkdown p,
.stApp:has(.lm-method-flag) .block-container [data-testid="stCaptionContainer"],
.stApp:has(.lm-method-flag) .block-container [data-testid="stExpander"] {
  max-width: 760px;
}
.stApp:has(.lm-method-flag) .lm-cons-grid,
.stApp:has(.lm-method-flag) .lm-cvrp-panel {
  max-width: 760px;
  margin-left: 0;
  margin-right: auto;
}
.stApp:has(.lm-method-flag) .lm-section {
  margin-top: 1.15rem;
  margin-bottom: 0.35rem;
  padding-bottom: 0.28rem;
}
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
  font-size: 13px;
  line-height: 1.35;
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
  font-size: 0.92rem;
  white-space: nowrap;
}
.lm-table tbody th {
  color: #111827;
  font-weight: 650;
  background: #F8FAFC;
}
.lm-table .lm-num {
  text-align: right;
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
div[data-testid="stMetricLabel"] p {
  white-space: normal; overflow: visible; text-overflow: clip;
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
@media (max-width: 760px) {
  .lm-hero { grid-template-columns: 1fr; padding: 1.4rem; min-height: auto; }
  .lm-route-motif { display: none; }
  .lm-vehicle-grid { grid-template-columns: 1fr; }
  .lm-vehicle-grid .lm-route-cell { grid-column: 1; }
  .lm-lang-wrap { margin-bottom: 0.4rem; }
}
.lm-inner h1 { font-size: 28px; font-weight: 700; margin-bottom: 0.35rem; color: var(--lm-ink); }
.lm-inner p { color: var(--lm-muted); margin-bottom: 0.85rem; font-size: 15px; line-height: 1.55; }
[data-testid="stCaptionContainer"] { font-size: 13px !important; color: var(--lm-muted); }
.stMarkdown p { max-width: 72ch; font-size: 15px; line-height: 1.55; }
.lm-table-wrap { max-height: 480px; }
.lm-table thead { position: sticky; top: 0; }
.lm-inner p { margin-bottom: .5rem; }
@media (max-width: 1449px) {
  .st-key-plan-pair [data-testid="stHorizontalBlock"] { flex-direction: column; }
  .st-key-plan-pair [data-testid="stColumn"] { width: 100% !important; }
}
@media (max-width: 1100px) {
  .lm-concept-grid, .lm-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  .lm-concept-grid, .lm-kpi-grid, .lm-cons-grid { grid-template-columns: 1fr; }
  .lm-cons-grid .lm-card:nth-child(-n+3),
  .lm-cons-grid .lm-card:nth-child(n+4) { grid-column: span 1; }
}

.lm-cvrp-panel {
  text-align: center;
  margin: 8px auto 1.5rem;
  max-width: 720px;
}
.lm-cvrp-panel .lm-cvrp,
.lm-cvrp-panel .lm-assign {
  width: 100%;
  max-width: 720px;
  height: auto;
  display: block;
  margin: 0 auto;
}
.lm-cvrp-panel .lm-cvrp-cap,
.lm-cvrp-panel .lm-cvrp-note {
  margin: 0.5rem auto 0;
  max-width: 640px;
  text-align: center;
  color: var(--lm-muted);
  font-size: 13.5px;
  line-height: 1.45;
}
.lm-cvrp-panel .lm-cvrp-note {
  margin-top: 0.2rem;
  font-size: 12.5px;
}

/* Overview: depot, customers, nearest-neighbour, then optimized routes. */
.lm-cvrp-depot { opacity: 0; animation: lm-loop-depot 10s ease-in-out infinite; }
.lm-cvrp-nodes circle { opacity: 0; animation: lm-loop-nodes 10s ease-in-out infinite; }
.lm-cvrp-nodes circle:nth-child(2) { animation-delay: 0.08s; }
.lm-cvrp-nodes circle:nth-child(3) { animation-delay: 0.14s; }
.lm-cvrp-nodes circle:nth-child(4) { animation-delay: 0.2s; }
.lm-cvrp-baseline path {
  fill: none; stroke: #94A3B8; stroke-width: 2.2;
  stroke-dasharray: 4000; stroke-dashoffset: 4000; opacity: 0;
  animation: lm-loop-baseline 10s ease-in-out infinite;
}
.lm-cvrp-routes path {
  fill: none; stroke-width: 3.2; stroke-linejoin: round; stroke-linecap: round;
  stroke-dasharray: 520; stroke-dashoffset: 520; opacity: 0;
  animation: lm-loop-route 10s ease-in-out infinite;
}
.lm-cvrp-routes path:nth-child(2) { animation-delay: 0.16s; }
.lm-cvrp-routes path:nth-child(3) { animation-delay: 0.3s; }
.lm-cvrp-routes path:nth-child(4) { animation-delay: 0.44s; }
.lm-cvrp-stops { opacity: 0; animation: lm-loop-stops 10s ease-in-out infinite; }
.lm-cvrp-stage-nn { opacity: 0; animation: lm-loop-stage-nn 10s ease-in-out infinite; }
.lm-cvrp-stage-opt { opacity: 0; animation: lm-loop-stage-opt 10s ease-in-out infinite; }
.lm-cvrp-stage-result { opacity: 0; animation: lm-loop-result 10s ease-in-out infinite; }
.lm-cvrp-stage-what { opacity: 0; animation: lm-loop-what 10s ease-in-out infinite; }
.lm-cvrp-dot-nn, .lm-cvrp-dot-opt {
  fill: #173B57; offset-rotate: 0deg;
}
.lm-cvrp-dot-nn {
  offset-path: url(#lm-nn-track);
  animation: lm-dot-nn 10s linear infinite;
}
.lm-cvrp-dot-opt {
  offset-path: url(#lm-opt-track);
  animation: lm-dot-opt 10s linear infinite;
}
@keyframes lm-loop-depot {
  0% { opacity: 0; } 8% { opacity: 1; } 92% { opacity: 1; } 100% { opacity: 0.2; }
}
@keyframes lm-loop-nodes {
  0%, 8% { opacity: 0; } 18% { opacity: 1; } 92% { opacity: 1; } 100% { opacity: 0.2; }
}
@keyframes lm-loop-baseline {
  0%, 16% { stroke-dashoffset: 4000; opacity: 0; }
  34% { stroke-dashoffset: 0; opacity: 0.72; }
  42% { stroke-dashoffset: 0; opacity: 0.16; }
  92% { opacity: 0.08; } 100% { opacity: 0; }
}
@keyframes lm-loop-stage-nn {
  0%, 16% { opacity: 0; } 20% { opacity: 1; } 40% { opacity: 1; } 45%, 100% { opacity: 0; }
}
@keyframes lm-loop-route {
  0%, 44% { stroke-dashoffset: 520; opacity: 0; }
  62% { stroke-dashoffset: 0; opacity: 1; }
  92% { stroke-dashoffset: 0; opacity: 1; }
  100% { stroke-dashoffset: 0; opacity: 0.2; }
}
@keyframes lm-loop-stops {
  0%, 54% { opacity: 0; } 64% { opacity: 1; } 92% { opacity: 1; } 100% { opacity: 0.2; }
}
@keyframes lm-loop-stage-opt {
  0%, 46% { opacity: 0; } 52% { opacity: 1; } 92% { opacity: 1; } 100% { opacity: 0; }
}
@keyframes lm-loop-result {
  0%, 74% { opacity: 0; } 80% { opacity: 1; } 92% { opacity: 1; } 100% { opacity: 0; }
}
@keyframes lm-loop-what {
  0%, 74% { opacity: 0; } 80% { opacity: 1; } 92% { opacity: 1; } 100% { opacity: 0; }
}
@keyframes lm-dot-nn {
  0%, 18% { offset-distance: 0%; opacity: 0; }
  20% { opacity: 1; offset-distance: 0%; }
  36% { opacity: 1; offset-distance: 100%; }
  40%, 100% { opacity: 0; offset-distance: 100%; }
}
@keyframes lm-dot-opt {
  0%, 46% { offset-distance: 0%; opacity: 0; }
  48% { opacity: 1; offset-distance: 0%; }
  76% { opacity: 1; offset-distance: 100%; }
  80%, 100% { opacity: 0; offset-distance: 100%; }
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
  92% { opacity: 0.28; } 100% { opacity: 0; }
}
@keyframes lm-assign-bars {
  0%, 22% { opacity: 0; } 30% { opacity: 1; } 92% { opacity: 1; } 100% { opacity: 0.2; }
}
@keyframes lm-assign-fill {
  0%, 28% { transform: scaleX(0); }
  44% { transform: scaleX(1); }
  92% { transform: scaleX(1); }
  100% { transform: scaleX(0); }
}
@keyframes lm-assign-route {
  0%, 48% { stroke-dashoffset: 420; opacity: 0; }
  68% { stroke-dashoffset: 0; opacity: 1; }
  92% { stroke-dashoffset: 0; opacity: 1; }
  100% { stroke-dashoffset: 0; opacity: 0.2; }
}
@keyframes lm-assign-label {
  0%, 52% { opacity: 0; } 60% { opacity: 1; } 92% { opacity: 1; } 100% { opacity: 0; }
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
  .lm-cvrp-depot, .lm-cvrp-nodes circle, .lm-cvrp-baseline path,
  .lm-cvrp-routes path, .lm-cvrp-stops, .lm-cvrp-stage-opt,
  .lm-cvrp-stage-result, .lm-cvrp-stage-what { opacity: 1 !important; }
  .lm-cvrp-stage-nn, .lm-cvrp-dot-nn, .lm-cvrp-dot-opt,
  .lm-assign-sheet, .lm-assign-sheet-label { opacity: 0 !important; }
  .lm-cvrp-baseline path, .lm-cvrp-routes path, .lm-assign-routes path {
    stroke-dashoffset: 0 !important;
  }
  .lm-assign-orders, .lm-assign-bars, .lm-assign-label { opacity: 1 !important; }
  .lm-assign-fill { transform: scaleX(1) !important; }
}
abbr.lm-tip {
  text-decoration: underline dotted;
  text-underline-offset: 2px;
  cursor: help;
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


BRAND_MARK_SVG = """
<svg viewBox="0 0 24 24" aria-hidden="true">
  <rect x="10" y="10" width="4" height="4" rx="0.6" fill="#4FD1C5"/>
  <circle cx="5" cy="6" r="1.7" fill="#93C5FD"/>
  <circle cx="19" cy="7" r="1.7" fill="#FDBA74"/>
  <circle cx="18" cy="18" r="1.7" fill="#C4B5FD"/>
  <path d="M12 12 L5 6 M12 12 L19 7 M12 12 L18 18" fill="none" stroke="#99F6E4" stroke-width="1.3"/>
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
    extra: str | None = None,
    context: str | None = None,
    compact: bool = True,
) -> None:
    if compact:
        st.markdown(
            f'<div class="lm-inner"><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>',
            unsafe_allow_html=True,
        )
        return
    kicker_html = f'<div class="lm-kicker">{escape(kicker)}</div>' if kicker else ""
    extra_html = f"<p>{escape(extra)}</p>" if extra else ""
    context_html = f'<p class="lm-hero-context">{escape(context)}</p>' if context else ""
    st.markdown(
        f"""
        <div class="lm-hero">
          <div class="lm-hero-content">
            {kicker_html}
            <h1>{escape(title)}</h1>
            <p>{escape(subtitle)}</p>
            {extra_html}
            {context_html}
          </div>
          <div class="lm-route-motif" aria-hidden="true">{BRAND_MARK_SVG}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, caption: str | None = None) -> None:
    caption_html = f"<p>{escape(caption)}</p>" if caption else ""
    st.markdown(
        f'<div class="lm-section"><h2>{escape(title)}</h2>{caption_html}</div>',
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


def concept_cards(items: list[tuple[str, str]]) -> None:
    cards = "".join(
        f'<article class="lm-card"><h3>{escape(title)}</h3><p>{body}</p></article>'
        for title, body in items
    )
    st.markdown(f'<div class="lm-concept-grid">{cards}</div>', unsafe_allow_html=True)


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


def cvrp_animation_html(result_label: str, aria_label: str) -> str:
    depot = escape(t("ux.over.anim.depot"))
    baseline = escape(t("ux.over.anim.baseline"))
    optimized = escape(t("ux.over.anim.optimized"))
    baseline_km = escape(t("ux.over.anim.km"))
    result = escape(result_label)
    what = escape(t("ux.over.anim.what"))
    return f"""
    <div class="lm-cvrp-panel">
    <svg class="lm-cvrp" viewBox="0 0 640 360" role="img" aria-label="{escape(aria_label)}">
      <defs>
        <path id="lm-nn-track" d="M320 175 L200 70 L445 65 L140 95 L520 100 L175 145
          L500 250 L125 245 L545 285 L155 305 L430 295 L485 155 L200 265 Z"/>
        <path id="lm-opt-track" d="M320 175 L200 70 L140 95 L175 145 L320 175 L445 65
          L520 100 L485 155 L320 175 L500 250 L545 285 L430 295 L320 175 L200 265
          L125 245 L155 305 L320 175"/>
      </defs>
      <g class="lm-cvrp-baseline">
        <path d="M320 175 L200 70 L445 65 L140 95 L520 100 L175 145 L500 250
          L125 245 L545 285 L155 305 L430 295 L485 155 L200 265 Z"/>
      </g>
      <g class="lm-cvrp-routes" fill="none">
        <path stroke="#2563EB" d="M320 175 L200 70 L140 95 L175 145 Z"/>
        <path stroke="#EA580C" d="M320 175 L445 65 L520 100 L485 155 Z"/>
        <path stroke="#7C3AED" d="M320 175 L500 250 L545 285 L430 295 Z"/>
        <path stroke="#C026D3" d="M320 175 L200 265 L125 245 L155 305 Z"/>
      </g>
      <circle class="lm-cvrp-dot-nn" r="5.5"/>
      <circle class="lm-cvrp-dot-opt" r="5.5"/>
      <g class="lm-cvrp-nodes" fill="#64748B">
        <circle cx="200" cy="70" r="5"/><circle cx="140" cy="95" r="5"/>
        <circle cx="175" cy="145" r="5"/><circle cx="445" cy="65" r="5"/>
        <circle cx="520" cy="100" r="5"/><circle cx="485" cy="155" r="5"/>
        <circle cx="500" cy="250" r="5"/><circle cx="545" cy="285" r="5"/>
        <circle cx="430" cy="295" r="5"/><circle cx="200" cy="265" r="5"/>
        <circle cx="125" cy="245" r="5"/><circle cx="155" cy="305" r="5"/>
      </g>
      <g class="lm-cvrp-stops" font-size="10" font-weight="700"
        text-anchor="middle" fill="#FFFFFF">
        <circle cx="200" cy="70" r="9" fill="#2563EB"/><text x="200" y="74">1</text>
        <circle cx="140" cy="95" r="9" fill="#2563EB"/><text x="140" y="99">2</text>
        <circle cx="175" cy="145" r="9" fill="#2563EB"/><text x="175" y="149">3</text>
        <circle cx="445" cy="65" r="9" fill="#EA580C"/><text x="445" y="69">1</text>
        <circle cx="520" cy="100" r="9" fill="#EA580C"/><text x="520" y="104">2</text>
        <circle cx="485" cy="155" r="9" fill="#EA580C"/><text x="485" y="159">3</text>
        <circle cx="500" cy="250" r="9" fill="#7C3AED"/><text x="500" y="254">1</text>
        <circle cx="545" cy="285" r="9" fill="#7C3AED"/><text x="545" y="289">2</text>
        <circle cx="430" cy="295" r="9" fill="#7C3AED"/><text x="430" y="299">3</text>
        <circle cx="200" cy="265" r="9" fill="#C026D3"/><text x="200" y="269">1</text>
        <circle cx="125" cy="245" r="9" fill="#C026D3"/><text x="125" y="249">2</text>
        <circle cx="155" cy="305" r="9" fill="#C026D3"/><text x="155" y="309">3</text>
      </g>
      <g class="lm-cvrp-depot">
        <rect x="310" y="165" width="20" height="20" rx="3" fill="#173B57"/>
        <text x="320" y="204" text-anchor="middle" fill="#173B57" font-size="13">{depot}</text>
      </g>
      <g class="lm-cvrp-stage-nn" text-anchor="middle" fill="#475569">
        <text x="320" y="28" font-size="14" font-weight="600">{baseline}</text>
        <text x="320" y="48" font-size="13">{baseline_km}</text>
      </g>
      <g class="lm-cvrp-stage-opt" text-anchor="middle" fill="#173B57">
        <text x="320" y="28" font-size="14" font-weight="600">{optimized}</text>
      </g>
      <g class="lm-cvrp-stage-result" text-anchor="middle" fill="#173B57">
        <text x="320" y="48" font-size="14" font-weight="700">{result}</text>
      </g>
      <g class="lm-cvrp-stage-what" text-anchor="middle" fill="#475569">
        <text x="320" y="338" font-size="12">{what}</text>
      </g>
    </svg>
    <p class="lm-cvrp-cap">{escape(t("ux.over.diagram"))}</p>
    <p class="lm-cvrp-note">{escape(t("ux.over.diagram.note"))}</p>
    </div>
    """


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
      <text class="lm-assign-label" x="320" y="28" text-anchor="middle"
        fill="#173B57" font-size="14" font-weight="600">{label}</text>
    </svg>
    <p class="lm-cvrp-cap">{caption}</p>
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
