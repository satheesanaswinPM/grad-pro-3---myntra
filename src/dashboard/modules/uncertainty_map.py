"""Questions still open after wishlisting."""

from __future__ import annotations

from src.dashboard.components import banner, show_theme_evidence, theme_table
from src.dashboard.load import Store


def render(store: Store) -> None:
    import streamlit as st

    st.header("Uncertainty map")
    banner()
    st.caption("Needs are unanswered questions after 'I like this.' They are not keyword clouds.")
    needs = store.themes_for("need")
    theme_table(needs)
    if not needs:
        st.warning("No need themes.")
        return
    labels = [str(row.get("theme_id")) for row in needs]
    chosen = st.selectbox("Open need evidence", labels)
    theme = next(row for row in needs if row.get("theme_id") == chosen)
    show_theme_evidence(store, theme)
