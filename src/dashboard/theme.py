"""Visual reskin matching the Stitch-generated "Discovery Console" reference design.

Scoped entirely to this app's own page via st.markdown -- this is a separate Streamlit process
from the MVP (src/mvp/), so this never touches that app's Myntra-pink light theme. CSS-only reskin,
not a rebuild: every table, chart, and expander stays the real Streamlit/Store-driven component --
only typography, color, spacing, and the evidence-card/status-pill markup change. No number, quote,
or label rendered by this reskin is invented; everything still comes from src/dashboard/load.py.
Palette and type scale taken directly from the Stitch DESIGN.md (instrument-grade analytics console).
"""

from __future__ import annotations

import streamlit as st

CANVAS = "#0B132B"
SURFACE_1 = "#131F37"
SURFACE_2 = "#1B2A4A"
BORDER = "#1E293B"
BORDER_STRONG = "#334155"
PRIMARY = "#14B8A6"
PRIMARY_HOVER = "#0F766E"
AMBER = "#F59E0B"
TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#94A3B8"
TEXT_DIM = "#64748B"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {{
  --canvas: {CANVAS};
  --surface-1: {SURFACE_1};
  --surface-2: {SURFACE_2};
  --border: {BORDER};
  --border-strong: {BORDER_STRONG};
  --primary: {PRIMARY};
  --amber: {AMBER};
  --text: {TEXT_PRIMARY};
  --text-secondary: {TEXT_SECONDARY};
  --text-dim: {TEXT_DIM};
}}

/* Base type -- Inter for structure, everywhere else falls back to it */
html, body, [class*="css"], [data-testid="stAppViewContainer"], .stApp,
.stMarkdown, .stMarkdown p, .stMarkdown li, [data-testid="stCaptionContainer"] {{
  font-family: 'Inter', sans-serif !important;
  color: var(--text) !important;
}}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"] {{
  background-color: var(--canvas) !important;
}}

/* Headlines */
h1, h2, h3, h4,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {{
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  letter-spacing: -0.01em;
  color: var(--text) !important;
}}

/* Monospace for data: metrics, dataframes, code, captions carrying record ids/labels */
[data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"],
.stDataFrame, .stDataFrame *, code, [data-testid="stCaptionContainer"] {{
  font-family: 'JetBrains Mono', monospace !important;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
  background-color: var(--surface-1) !important;
  border-right: 1px solid var(--border);
}}
[data-testid="stSidebar"] h1 {{
  color: var(--primary) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-weight: 600 !important;
}}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
  color: var(--text-dim) !important;
}}
/* Sidebar nav (radio) rows */
[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
  border-radius: 4px;
  padding: 0.15rem 0.4rem;
}}
[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {{
  background-color: var(--surface-2);
  color: var(--primary) !important;
}}
[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {{
  color: var(--primary) !important;
  font-weight: 600;
}}

/* Metric tiles (KPI cards) */
div[data-testid="stMetric"] {{
  background-color: var(--surface-1) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  padding: 0.75rem 0.9rem !important;
}}
div[data-testid="stMetricLabel"] {{
  color: var(--text-dim) !important;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.68rem !important;
}}
div[data-testid="stMetricValue"] {{
  color: var(--text) !important;
}}

/* Bordered containers (cards) */
div[data-testid="stVerticalBlockBorderWrapper"] {{
  background-color: var(--surface-1) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
}}

/* Info / warning / error banners */
div[data-testid="stAlert"] {{
  background-color: var(--surface-1) !important;
  border: 1px solid var(--border-strong) !important;
  border-left: 2px solid var(--primary) !important;
  border-radius: 4px !important;
  color: var(--text) !important;
}}
div[data-testid="stAlert"] p {{
  color: var(--text) !important;
}}

/* Buttons */
.stButton > button {{
  background-color: var(--surface-2) !important;
  border: 1px solid var(--border-strong) !important;
  color: var(--text) !important;
  border-radius: 4px !important;
  font-family: 'JetBrains Mono', monospace !important;
}}
.stButton > button:hover {{
  border-color: var(--primary) !important;
  color: var(--primary) !important;
}}
.stButton > button[kind="primary"] {{
  background-color: var(--primary) !important;
  border: none !important;
  color: #00201c !important;
  font-weight: 600 !important;
}}
.stButton > button[kind="primary"]:hover {{
  background-color: var(--primary-hover, #0F766E) !important;
  color: white !important;
}}

/* Expanders (Full feedback text) */
div[data-testid="stExpander"] {{
  background-color: var(--surface-1) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
}}
div[data-testid="stExpander"] summary {{
  color: var(--text-secondary) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.85rem;
}}

/* Inputs */
div[data-baseweb="select"] div, [data-testid="stTextInput"] input,
[data-testid="stTextInput"] div {{
  background-color: var(--surface-1) !important;
  color: var(--text) !important;
  border-color: var(--border-strong) !important;
  border-radius: 4px !important;
  font-family: 'JetBrains Mono', monospace !important;
}}
div[data-baseweb="popover"] li, div[data-baseweb="menu"], ul[role="listbox"] {{
  background-color: var(--surface-2) !important;
  color: var(--text) !important;
}}

/* Dividers */
[data-testid="stMarkdownContainer"] hr {{
  border-color: var(--border) !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {{
  color: var(--primary) !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{
  background-color: var(--primary) !important;
}}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def status_pill(status: str) -> str:
    """Small teal/amber status badge -- 'observed evidence' vs 'hypothesis', matching the Stitch tag spec."""
    observed = status == "observed_evidence"
    label = "observed" if observed else "hypothesis"
    color = PRIMARY if observed else AMBER
    bg = "rgba(20, 184, 166, 0.1)" if observed else "rgba(245, 158, 11, 0.1)"
    border = "rgba(20, 184, 166, 0.4)" if observed else "rgba(245, 158, 11, 0.4)"
    return (
        f'<span style="display:inline-block;background:{bg};color:{color};border:1px solid {border};'
        f'font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.03em;padding:0.1rem 0.45rem;border-radius:2px;">{label}</span>'
    )


def meta_tag(text: str) -> str:
    """Neutral metadata chip -- source/category/journey-stage labels in an evidence card header."""
    return (
        f'<span style="color:{TEXT_SECONDARY};font-family:\'JetBrains Mono\',monospace;'
        f'font-size:0.78rem;">{text}</span>'
    )
