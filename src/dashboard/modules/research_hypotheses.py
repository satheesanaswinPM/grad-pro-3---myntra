"""Testable follow-ups for primary research."""

from __future__ import annotations

from src.dashboard.components import banner, open_evidence, quote_cards
from src.dashboard.load import Store, split_ids
from src.qualify.config import ROOT
from src.score.schema import TOP_HYPOTHESES
from src.score.statements import copy_for


def render(store: Store) -> None:
    import streamlit as st

    st.header("Research hypotheses")
    banner()
    st.caption("These are primary-research asks, not product specs and not a discount brief.")
    path = ROOT / "reports" / "research_hypotheses.md"
    if path.exists():
        with st.expander("Full hypothesis report"):
            st.markdown(path.read_text(encoding="utf-8"))

    for row in store.opportunities[:TOP_HYPOTHESES]:
        text = copy_for(str(row.get("label") or ""), str(row.get("extractor") or ""), str(row.get("label") or ""))
        st.subheader(f"H{row.get('rank')}. {row.get('opportunity_id')}")
        st.markdown(f"**Hypothesis:** {text['statement']}")
        st.markdown(f"**Ask:** {text['ask']}")
        st.markdown(f"**Success signal:** {text['signal']}")
        st.caption(
            f"n={row.get('unique_records')} / {row.get('denominator')} relevant ({row.get('pct_relevant')}%). "
            f"Conversion link: {row.get('conversion_link_status')}."
        )
        open_evidence(
            split_ids(row.get("evidence_record_ids")),
            str(row.get("opportunity_id")),
            theme_ids=str(row.get("theme_ids") or ""),
            key_prefix="hyp-",
        )
        with st.expander("Sample evidence"):
            quote_cards(store.insights_for_opportunity(row, limit=5))
