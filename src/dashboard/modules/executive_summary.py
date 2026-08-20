"""Dataset size, sources, key findings, top opportunities."""

from __future__ import annotations

from src.dashboard.components import banner, open_evidence, opportunity_table, pct, quote_cards
from src.dashboard.load import Store, split_ids


def render(store: Store) -> None:
    import streamlit as st

    st.header("Executive summary")
    banner()
    st.subheader("Research question")
    st.markdown(
        "Who adds products to a wishlist, why they do it, what prevents purchase, what information is still "
        "missing, which barriers matter most, and **which opportunity Growth should investigate first** to "
        "improve 30-day wishlist-to-purchase conversion — without using discounts as the lever."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Canonical records", f"{store.n_canonical:,}")
    c2.metric("Relevant records", f"{store.n_relevant:,}", pct(store.n_relevant, store.n_canonical or store.n_relevant))
    extracted = store.manifests.get("phase4", {}).get("n_extracted_records") or len(store.by_record)
    c3.metric("Records with extractions", f"{extracted:,}", pct(int(extracted), store.n_relevant))
    c4.metric("Ranked opportunities", str(len(store.opportunities)))

    st.caption("Relevant is the denominator for later percentages. Non-English rows were not dropped.")
    st.markdown("**Source mix (relevant)**")
    st.dataframe(
        [{"source": name, "n relevant": n, "% relevant": pct(n, store.n_relevant)} for name, n in store.source_counts()],
        hide_index=True,
        width="stretch",
    )

    st.subheader("Investigate first")
    if store.opportunities:
        top = store.opportunities[0]
        st.markdown(
            f"**{top.get('opportunity_id')}** (rank 1, total {top.get('total_score')} / 5) — "
            f"{top.get('problem_statement')}"
        )
        st.markdown(f"User still needs: *{top.get('user_need')}*")
        st.caption(
            f"n={top.get('unique_records')} / {top.get('denominator')} relevant "
            f"({top.get('pct_relevant')}%). Status {top.get('status')}. "
            f"Conversion link: {top.get('conversion_link_status')}."
        )
        open_evidence(
            split_ids(top.get("evidence_record_ids")),
            str(top.get("opportunity_id")),
            theme_ids=str(top.get("theme_ids") or ""),
        )
        quote_cards(store.insights_for_opportunity(top, limit=6))

    st.subheader("Top opportunities")
    opportunity_table(store, store.opportunities[:8])
    st.caption("Scores are not rescaled to the current leader. Frequency uses relevant, not the full scrape.")
