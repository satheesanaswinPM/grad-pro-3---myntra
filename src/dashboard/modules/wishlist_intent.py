"""Why users wishlist; mix by source and category."""

from __future__ import annotations

from src.dashboard.components import banner, show_theme_evidence, theme_table
from src.dashboard.load import Store, mix_dict


def render(store: Store) -> None:
    import streamlit as st

    st.header("Wishlist intent")
    banner()
    st.caption("Intent labels come from Phase 3 extractions. They are not a finding until they recur with evidence.")
    intents = store.themes_for("intent")
    theme_table(intents)
    if not intents:
        st.warning("No intent themes. Re-run Phase 3–4.")
        return
    labels = [str(row.get("theme_id")) for row in intents]
    chosen = st.selectbox("Open intent evidence", labels)
    theme = next(row for row in intents if row.get("theme_id") == chosen)
    st.markdown("**Source mix for this intent**")
    mix = mix_dict(theme.get("source_mix"))
    st.dataframe(
        [{"source": name, "unique records": n} for name, n in sorted(mix.items(), key=lambda item: -item[1])],
        hide_index=True,
        width="stretch",
    )
    st.markdown("**Category mix**")
    cats = mix_dict(theme.get("category_mix"))
    st.dataframe(
        [{"category": name, "unique records": n} for name, n in sorted(cats.items(), key=lambda item: -item[1])],
        hide_index=True,
        width="stretch",
    )
    show_theme_evidence(store, theme)
