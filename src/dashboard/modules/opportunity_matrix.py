"""Frequency × severity/impact × evidence confidence."""

from __future__ import annotations

from src.dashboard.components import banner, open_evidence, opportunity_table, quote_cards
from src.dashboard.load import Store, split_ids


def render(store: Store) -> None:
    import streamlit as st

    st.header("Opportunity matrix")
    banner()
    st.caption(
        "X = frequency (share of relevant, saturated at 20%). Y = severity. "
        "Point size = evidence confidence. Conversion link is a hypothesis."
    )
    opportunity_table(store)
    chart_rows = [
        {
            "frequency": float(row.get("frequency") or 0),
            "severity": float(row.get("severity") or 0),
            "evidence_confidence": float(row.get("evidence_confidence") or 0),
            "opportunity": str(row.get("opportunity_id")),
        }
        for row in store.opportunities
        if row.get("status") == "observed_evidence"
    ]
    if chart_rows:
        st.scatter_chart(
            chart_rows,
            x="frequency",
            y="severity",
            color="opportunity",
            size="evidence_confidence",
        )
    opp = None
    labels = [str(row.get("opportunity_id")) for row in store.opportunities]
    if labels:
        chosen = st.selectbox("Open opportunity evidence", labels)
        opp = next(row for row in store.opportunities if row.get("opportunity_id") == chosen)
    if opp:
        st.markdown(f"**{opp.get('problem_statement')}**")
        st.markdown(f"Need: *{opp.get('user_need')}*")
        st.caption(
            f"total {opp.get('total_score')}/5 · n={opp.get('unique_records')} relevant ({opp.get('pct_relevant')}%) · "
            f"conversion `{opp.get('conversion_link_status')}`"
        )
        open_evidence(split_ids(opp.get("evidence_record_ids")), str(opp.get("opportunity_id")), str(opp.get("theme_ids") or ""))
        quote_cards(store.insights_for_opportunity(opp, limit=10))
