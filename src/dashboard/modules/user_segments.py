"""Segment definitions, size, behaviors, dominant barriers, and needs."""

from __future__ import annotations

from src.dashboard.components import banner, open_evidence, quote_cards
from src.dashboard.load import Store, split_ids


def render(store: Store) -> None:
    import streamlit as st

    st.header("User segments")
    banner()
    st.caption("Segments exist only when synthesis found recurring observed evidence. They are not invented personas.")
    if not store.segments:
        st.warning("No segments earned existence.")
        return
    st.dataframe(
        [
            {
                "segment": row.get("label"),
                "n": row.get("unique_records"),
                "% relevant": row.get("pct_relevant"),
                "denominator": row.get("denominator_label"),
                "dominant barriers": row.get("dominant_barriers"),
                "dominant needs": row.get("dominant_needs"),
                "status": row.get("status"),
            }
            for row in store.segments
        ],
        hide_index=True,
        width="stretch",
    )
    labels = [str(row.get("label")) for row in store.segments]
    chosen = st.selectbox("Open segment evidence", labels)
    segment = next(row for row in store.segments if row.get("label") == chosen)
    st.markdown(f"**Definition:** {segment.get('definition')}")
    st.caption(
        f"{segment.get('unique_records')} unique observed records / {segment.get('denominator')} relevant "
        f"({segment.get('pct_relevant')}%)."
    )
    ids = split_ids(segment.get("evidence_record_ids"))
    open_evidence(ids, f"segment:{segment.get('label')}")
    quote_cards(store.insights_for(ids, limit=12))
