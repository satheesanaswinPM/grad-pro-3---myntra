"""Where users go off-platform and why."""

from __future__ import annotations

from collections import Counter

from src.dashboard.components import banner, open_evidence, pct, quote_cards, show_theme_evidence, theme_table
from src.dashboard.load import Store, split_ids


def render(store: Store) -> None:
    import streamlit as st

    st.header("External research")
    banner()
    st.caption("Phase 2 flags destinations mentioned in the text. Phase 3 behaviors add evidence-linked labels.")
    dest: Counter[str] = Counter()
    for row in store.relevant.values():
        for name in str(row.get("external_destinations") or "").split("|"):
            if name:
                dest[name] += 1
    st.dataframe(
        [{"destination": name, "relevant records": n, "% relevant": pct(n, store.n_relevant)} for name, n in dest.most_common()],
        hide_index=True,
        width="stretch",
    )
    opp = store.opportunity("opp:external_research")
    if opp:
        st.markdown(f"**Scored opportunity:** `{opp.get('opportunity_id')}` rank {opp.get('rank')} · total {opp.get('total_score')}/5")
        st.markdown(opp.get("problem_statement") or "")
        open_evidence(split_ids(opp.get("evidence_record_ids")), str(opp.get("opportunity_id")), str(opp.get("theme_ids") or ""))
        quote_cards(store.insights_for_opportunity(opp, limit=8))

    themes = [row for row in store.themes if str(row.get("label") or "").startswith("external:")]
    theme_table(themes)
    if themes:
        labels = [str(row.get("theme_id")) for row in themes]
        chosen = st.selectbox("Open destination evidence", labels)
        theme = next(row for row in themes if row.get("theme_id") == chosen)
        show_theme_evidence(store, theme)
