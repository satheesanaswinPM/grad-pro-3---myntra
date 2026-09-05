"""Visual reskin matching the Stitch-generated reference design ("Elevated Runway Commerce").

Scoped entirely to this app's own page via st.markdown -- each Streamlit app is its own process,
so this never touches the separate research console (src/dashboard/), which keeps its own dark
theme. This is a CSS-only reskin, not a rebuild: every interactive element stays a real Streamlit
widget wired to the existing Python logic in state.py/agent.py/catalog.py. Palette and type scale
taken directly from the Stitch DESIGN.md.
"""

from __future__ import annotations

import streamlit as st

PRIMARY = "#FF3F6C"  # Myntra's actual signature brand pink (was #D82054, a darker berry approximation)
PRIMARY_HOVER = "#E12E59"
INK = "#282C3F"
MUTED = "#535766"
SURFACE = "#FFFFFF"
SURFACE_SOFT = "#F5F5F6"
BORDER = "#EAEAEC"
SUCCESS = "#006540"
NAV_TEXT_MUTED = "#AFB6CC"  # muted/caption text tuned for the dark sidebar, not the light --muted

FONT_LINKS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Plus+Jakarta+Sans:'
    'wght@400;500;600;700&display=swap" rel="stylesheet">'
)

CSS = f"""
<style>
:root {{
  --primary: {PRIMARY};
  --primary-hover: {PRIMARY_HOVER};
  --ink: {INK};
  --muted: {MUTED};
  --surface: {SURFACE};
  --surface-soft: {SURFACE_SOFT};
  --border: {BORDER};
  --nav-text-muted: {NAV_TEXT_MUTED};
}}

/* Base type -- !important because Streamlit's own stylesheet loads with equal-specificity
   selectors later in source order and would otherwise win the cascade over an injected style tag.
   color is forced here too: Streamlit's dark-mode auto-detection (see below) sets light default
   text, which against this app's forced-white background was rendering as invisible white-on-white. */
html, body, [class*="css"], [data-testid="stAppViewContainer"], .stApp,
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p,
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label,
[data-testid="stCheckbox"] label p, [data-testid="stRadio"] label p,
.stTabs [data-baseweb="tab-list"] button p,
.stButton button, .stTextInput input, .stNumberInput input, .stSelectbox,
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] {{
  font-family: 'Plus Jakarta Sans', -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
  color: var(--ink) !important;
}}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{
  color: var(--muted) !important;
}}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
  background-color: var(--surface) !important;
}}

/* Headlines -- Bebas Neue, uppercase, condensed, matching the Stitch type scale */
h1, h2, h3,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stHeading"] {{
  font-family: 'Bebas Neue', Impact, 'Arial Narrow', sans-serif !important;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: var(--ink) !important;
}}
/* Sub-headings (####, e.g. "What actually differs" / "Why") -- bold Jakarta, not Bebas, so they
   read as body-level section markers rather than full display headlines, but still stand out. */
h4, h5, h6,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5,
[data-testid="stMarkdownContainer"] h6 {{
  font-family: 'Plus Jakarta Sans', -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
  font-weight: 700 !important;
  color: var(--ink) !important;
}}
/* Bold markdown (**text**) -- explicit weight so product titles / section labels are always
   visually distinct from surrounding body text, not left to font-fallback behavior. */
[data-testid="stMarkdownContainer"] strong,
.stMarkdown strong, .stMarkdown b {{
  font-weight: 700 !important;
  color: var(--ink) !important;
}}

/* Primary buttons -- solid pink CTA, matches "BUY THIS ONE" / "SAVE TO WISHLIST" */
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {{
  background-color: var(--primary) !important;
  border: none !important;
  color: white !important;
  font-weight: 700 !important;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  border-radius: 8px !important;
  padding: 0.6rem 1.2rem !important;
}}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover {{
  background-color: var(--primary-hover) !important;
  color: white !important;
}}
.stButton > button[kind="primary"]:disabled {{
  background-color: var(--border) !important;
  color: var(--muted) !important;
}}

/* Secondary buttons -- outlined ink, matches "KEEP" / "REMOVE" */
.stButton > button[kind="secondary"] {{
  background-color: var(--surface) !important;
  border: 1.5px solid var(--ink) !important;
  color: var(--ink) !important;
  font-weight: 700 !important;
  border-radius: 8px !important;
}}
.stButton > button[kind="secondary"]:hover {{
  border-color: var(--primary) !important;
  color: var(--primary) !important;
}}

/* Bordered containers (product cards, comparison cards) */
div[data-testid="stVerticalBlockBorderWrapper"] {{
  border-radius: 12px !important;
  border-color: var(--border) !important;
  box-shadow: 0 1px 8px rgba(40, 44, 63, 0.05);
}}

/* Metric stat tiles (Simulated day / Resolved / Still cold) */
div[data-testid="stMetric"] {{
  background-color: var(--surface-soft) !important;
  border-radius: 10px !important;
  padding: 0.75rem 0.9rem !important;
  border: 1px solid var(--border) !important;
}}
div[data-testid="stMetricLabel"] {{
  color: var(--muted) !important;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}}

/* Radio pills (reason chips) -- native accent-color for a pink selection dot */
div[data-testid="stRadio"] label {{
  accent-color: var(--primary);
}}
div[data-testid="stRadio"] > div {{
  gap: 0.4rem;
}}

/* Tabs -- current Streamlit renders these as [data-testid="stTab"] / role="tab", not the older
   BaseWeb tab-list markup. Inactive-tab text was inheriting Streamlit's dark-theme default
   (near-white, ~rgb(250,250,250)) over a transparent tab background showing the page's white
   behind it -- invisible text-on-background, same failure shape as the header/tab-list bug
   already fixed elsewhere in this file, just a different DOM shape. */
[data-testid="stTab"] p {{
  color: var(--ink) !important;
  font-weight: 600 !important;
}}
[data-testid="stTab"][aria-selected="true"] p {{
  color: var(--primary) !important;
  font-weight: 700 !important;
}}
[data-testid="stTab"] {{
  background-color: transparent !important;
}}
[role="tablist"] {{
  background-color: var(--surface) !important;
}}
[data-testid="stTab"] .react-aria-SelectionIndicator {{
  background-color: var(--primary) !important;
}}

/* Alerts -- rounded, softer corners to match card language */
div[data-testid="stAlert"] {{
  border-radius: 12px !important;
}}
/* Streamlit's default warning/info/error/success colors are tuned for a dark theme --
   e.g. warning text renders as pale yellow-white (~rgb(255,255,194)) on a barely-tinted
   yellow background, nearly invisible against this app's forced-light surface. Same
   failure shape as the header/tab bugs fixed above, just a different component. */
[data-testid="stAlertContentWarning"] {{
  background-color: #FFF3CD !important;
}}
[data-testid="stAlertContentWarning"] p,
[data-testid="stAlertContentWarning"] span {{
  color: #7A5200 !important;
}}
[data-testid="stAlertContentSuccess"] {{
  background-color: #E3F3EA !important;
}}
[data-testid="stAlertContentSuccess"] p,
[data-testid="stAlertContentSuccess"] span {{
  color: {SUCCESS} !important;
}}
[data-testid="stAlertContentError"] {{
  background-color: #FCE8E6 !important;
}}
[data-testid="stAlertContentError"] p,
[data-testid="stAlertContentError"] span {{
  color: #B3261E !important;
}}
[data-testid="stAlertContentInfo"] {{
  background-color: #E8F0FE !important;
}}
[data-testid="stAlertContentInfo"] p,
[data-testid="stAlertContentInfo"] span {{
  color: #1A56A0 !important;
}}

/* Sidebar / navigation -- deliberately darker than the rest of the app (the main surface is
   white). Every text rule below is necessary, not decorative: the base type rule at the top of
   this file forces `color: var(--ink)` (dark) globally, which would be invisible dark-on-dark
   against this now-dark sidebar background -- the exact bug already found and fixed twice
   elsewhere in this file (tabs, alerts), pre-empted here instead of discovered by a screenshot. */
[data-testid="stSidebar"] {{
  background-color: var(--ink) !important;
  border-right: none !important;
}}
[data-testid="stSidebar"] h1 {{
  color: var(--primary) !important;
}}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] .stMarkdown strong,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
  color: #FFFFFF !important;
}}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
  color: var(--nav-text-muted) !important;
}}
[data-testid="stSidebar"] hr {{
  border-color: rgba(255, 255, 255, 0.16) !important;
}}
/* Fast-forward control -- a light input/button reading as an inset control on the dark nav,
   the same "light control on dark surface" pattern the rest of the app already uses elsewhere.
   Must re-force dark text here: the broad white-text rule above also catches this button's own
   label (Streamlit renders it through the same stMarkdownContainer/<p> path as body text), which
   would otherwise leave white label text on this button's now-white background. */
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
  background-color: var(--surface) !important;
  border: 1.5px solid var(--surface) !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="secondary"] p {{
  color: var(--ink) !important;
}}

/* Inputs */
div[data-baseweb="select"] > div,
input {{
  border-radius: 8px !important;
}}

/* Force light widget chrome regardless of Streamlit's own dark/light auto-detection --
   this app must always render the Myntra-light look, independent of OS color-scheme.
   (The separate research console keeps whatever theme it already has -- this CSS is
   injected only into this app's own page and never reaches that one.) */
[data-testid="stHeader"] {{
  background-color: var(--surface) !important;
}}
[data-testid="stSelectbox"] div,
[data-testid="stNumberInput"] div,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] div,
[data-testid="stTextInput"] input,
[data-testid="stMultiSelect"] div {{
  background-color: var(--surface) !important;
  color: var(--ink) !important;
  border-color: var(--border) !important;
}}
[data-testid="stSelectbox"] svg,
[data-testid="stNumberInput"] svg {{
  fill: var(--ink) !important;
}}
/* BaseWeb portals (dropdown option lists) render outside the normal component tree */
div[data-baseweb="popover"] li,
div[data-baseweb="menu"],
ul[role="listbox"] {{
  background-color: var(--surface) !important;
  color: var(--ink) !important;
}}
</style>
"""


def inject_css() -> None:
    # Real <link> tags, not a CSS @import inside a dynamically-injected <style> block --
    # @import set via innerHTML/unsafe_allow_html is unreliable across browsers and can
    # silently fail to fetch even when the rest of the stylesheet applies fine.
    st.markdown(FONT_LINKS, unsafe_allow_html=True)
    st.markdown(CSS, unsafe_allow_html=True)


def pill(text: str, *, kind: str = "neutral") -> str:
    """Small rounded badge, e.g. the reason tag on a wishlist row or a staleness flag.
    kind: 'primary' (pink, e.g. recommended/nudge) | 'neutral' (gray, e.g. a reason tag)."""
    bg = "#FCE4EC" if kind == "primary" else SURFACE_SOFT
    color = PRIMARY if kind == "primary" else MUTED
    return (
        f'<span style="display:inline-block;background:{bg};color:{color};'
        f'font-size:0.72rem;font-weight:700;letter-spacing:0.02em;text-transform:uppercase;'
        f'padding:0.15rem 0.55rem;border-radius:999px;border:1px solid {BORDER};">{text}</span>'
    )
