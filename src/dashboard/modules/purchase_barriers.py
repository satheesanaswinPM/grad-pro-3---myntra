"""Ranked barriers with frequency, severity, and evidence."""

from __future__ import annotations

from src.dashboard.components import banner, open_evidence, pick_opportunity, quote_cards, show_theme_evidence, theme_table
from src.dashboard.load import Store, split_ids


def render(store: Store) -> None:
    import streamlit as st

    st.header("Purchase barriers")
    banner()
    st.caption("Barrier frequency is unique records / relevant. Severity lives on the opportunity score, not on mention volume.")
    barriers = store.themes_for("barrier")
    theme_table(barriers)
    barrier_opps = [
        row
        for row in store.opportunities
        if str(row.get("extractor")) == "barrier" or "barrier:" in str(row.get("theme_ids") or "")
    ]
    st.subheader("Scored barrier-led opportunities")
    st.dataframe(
        [
            {
                "rank": row.get("rank"),
                "opportunity": row.get("opportunity_id"),
                "total /5": row.get("total_score"),
                "severity": row.get("severity"),
                "hesitation": row.get("purchase_hesitation_link"),
                "n": row.get("unique_records"),
                "% relevant": row.get("pct_relevant"),
                "conversion link": row.get("conversion_link_status"),
            }
            for row in barrier_opps
        ],
        hide_index=True,
        width="stretch",
    )
    st.subheader("Evidence")
    mode = st.radio("Show evidence for", ("theme", "opportunity"), horizontal=True)
    if mode == "theme" and barriers:
        labels = [str(row.get("theme_id")) for row in barriers]
        chosen = st.selectbox("Barrier theme", labels)
        theme = next(row for row in barriers if row.get("theme_id") == chosen)
        show_theme_evidence(store, theme)
        return
    opp = pick_opportunity(store, key="barrier-opp")
    if opp:
        st.markdown(f"**{opp.get('problem_statement')}**")
        quote_cards(store.insights_for_opportunity(opp, limit=12))
        open_evidence(split_ids(opp.get("evidence_record_ids")), str(opp.get("opportunity_id")), str(opp.get("theme_ids") or ""))
