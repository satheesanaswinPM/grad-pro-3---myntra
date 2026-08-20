"""Attributes compared, alternatives, and decision criteria."""

from __future__ import annotations

from src.dashboard.components import banner, open_evidence, quote_cards, show_theme_evidence, theme_table
from src.dashboard.load import Store, split_ids


def render(store: Store) -> None:
    import streamlit as st

    st.header("Comparison behavior")
    banner()
    opp = store.opportunity("opp:comparison_loop")
    if opp:
        st.markdown(f"**Scored opportunity:** `{opp.get('opportunity_id')}` rank {opp.get('rank')} · total {opp.get('total_score')}/5")
        st.markdown(opp.get("problem_statement") or "")
        st.caption(
            f"n={opp.get('unique_records')} / {opp.get('denominator')} relevant ({opp.get('pct_relevant')}%). "
            f"Conversion link: {opp.get('conversion_link_status')}."
        )
        open_evidence(split_ids(opp.get("evidence_record_ids")), str(opp.get("opportunity_id")), str(opp.get("theme_ids") or ""))
        quote_cards(store.insights_for_opportunity(opp, limit=8))

    st.subheader("Comparison themes")
    themes = [
        row
        for row in store.themes
        if "comparison" in str(row.get("label") or "") or str(row.get("label")) == "better_alternative"
    ]
    theme_table(themes)
    if themes:
        labels = [str(row.get("theme_id")) for row in themes]
        chosen = st.selectbox("Open comparison theme", labels)
        theme = next(row for row in themes if row.get("theme_id") == chosen)
        show_theme_evidence(store, theme)
