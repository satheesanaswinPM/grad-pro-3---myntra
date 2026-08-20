"""Wishlist-to-purchase research console. Insight click-through to verbatim feedback."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.dashboard.load import Store
from src.dashboard.modules import (
    category_analysis,
    comparison_behavior,
    customer_journey,
    evidence_explorer,
    executive_summary,
    external_research,
    opportunity_matrix,
    purchase_barriers,
    research_hypotheses,
    solution_concepts,
    uncertainty_map,
    user_segments,
    wishlist_intent,
)

PAGES = (
    ("Executive summary", executive_summary.render),
    ("Wishlist intent", wishlist_intent.render),
    ("Purchase barriers", purchase_barriers.render),
    ("User segments", user_segments.render),
    ("Uncertainty map", uncertainty_map.render),
    ("Customer journey", customer_journey.render),
    ("Comparison behavior", comparison_behavior.render),
    ("External research", external_research.render),
    ("Category analysis", category_analysis.render),
    ("Opportunity matrix", opportunity_matrix.render),
    ("Evidence explorer", evidence_explorer.render),
    ("Research hypotheses", research_hypotheses.render),
    ("Solution concepts", solution_concepts.render),
)


@st.cache_resource(show_spinner="Loading research tables...")
def load_store() -> Store:
    return Store.build()


def main() -> None:
    st.set_page_config(page_title="Wishlist discovery console", layout="wide")
    st.sidebar.title("Discovery console")
    st.sidebar.caption("Myntra Growth · Part 1 · evidence over guesses")
    labels = [name for name, _fn in PAGES]
    if st.session_state.get("nav") not in labels:
        st.session_state["nav"] = labels[0]
    picked = st.sidebar.radio("Module", labels, key="nav")
    try:
        store = load_store()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()
    render = dict(PAGES)[picked]
    render(store)


if __name__ == "__main__":
    main()
