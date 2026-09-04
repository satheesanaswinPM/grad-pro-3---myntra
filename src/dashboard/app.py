"""Wishlist-to-purchase research console. Insight click-through to verbatim feedback."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.dashboard import theme
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


def _merge(*fns):
    """Stack two module renderers on one page, divided -- no changes to either module's own code."""

    def _render(store: Store) -> None:
        import streamlit as st

        for i, fn in enumerate(fns):
            if i > 0:
                st.divider()
            fn(store)

    return _render


# 13 original modules merged into 8 semantically-grouped pages for a shorter sidebar.
PAGES = (
    ("Executive summary", executive_summary.render),
    ("Intent & segments", _merge(wishlist_intent.render, user_segments.render)),
    ("Barriers & uncertainty", _merge(purchase_barriers.render, uncertainty_map.render)),
    ("Customer journey", customer_journey.render),
    ("Comparison & external research", _merge(comparison_behavior.render, external_research.render)),
    ("Opportunity & category analysis", _merge(opportunity_matrix.render, category_analysis.render)),
    ("Evidence explorer", evidence_explorer.render),
    ("Hypotheses & solutions", _merge(research_hypotheses.render, solution_concepts.render)),
)


@st.cache_resource(show_spinner="Loading research tables...")
def load_store() -> Store:
    return Store.build()


def main() -> None:
    st.set_page_config(page_title="Wishlist discovery console", layout="wide")
    theme.inject_css()
    st.sidebar.title("Discovery console")
    st.sidebar.caption("Myntra Growth · evidence over guesses")
    labels = [name for name, _fn in PAGES]
    if st.session_state.get("nav") not in labels:
        st.session_state["nav"] = labels[0]
    picked = st.session_state["nav"]
    for label in labels:
        is_active = picked == label
        if st.sidebar.button(
            label,
            key=f"nav_btn_{label}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            st.session_state["nav"] = label
            st.rerun()
    try:
        store = load_store()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()
    render = dict(PAGES)[picked]
    render(store)


if __name__ == "__main__":
    main()
