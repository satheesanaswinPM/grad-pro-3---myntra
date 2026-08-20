"""Click an insight, read the actual feedback. Do not hide evidence behind exports-only."""

from __future__ import annotations

from src.dashboard.components import banner, quote_cards
from src.dashboard.load import Store


def render(store: Store) -> None:
    import streamlit as st

    st.header("Evidence explorer")
    banner()
    title = st.session_state.get("evidence_title")
    focus_ids = st.session_state.get("evidence_ids")
    theme_ids = str(st.session_state.get("evidence_theme_ids") or "")
    forced_extractor = str(st.session_state.get("evidence_extractor") or "")
    if title:
        st.markdown(f"Focused on **{title}**")
        if st.button("Clear focus (search the full extracted corpus)"):
            for key in ("evidence_ids", "evidence_title", "evidence_theme_ids", "evidence_extractor"):
                st.session_state.pop(key, None)
            st.rerun()

    sources = sorted({str(row.get("source") or "") for row in store.relevant.values() if row.get("source")})
    categories = sorted({str(row.get("fashion_category") or "unlabeled") for row in store.relevant.values()})
    c1, c2, c3, c4 = st.columns(4)
    source = c1.selectbox("Source", ["(all)"] + sources)
    category = c2.selectbox("Category", ["(all)"] + categories)
    extractor_f = c3.selectbox("Extractor", ["(all)", "intent", "barrier", "need", "behavior"])
    status = c4.selectbox("Status", ["(all)", "observed_evidence", "hypothesis"])
    query = st.text_input("Search in quote or full text")
    extractor = "" if extractor_f == "(all)" else extractor_f
    if forced_extractor and extractor_f == "(all)":
        extractor = forced_extractor

    if focus_ids:
        insights = store.insights_for(
            list(focus_ids),
            theme_ids=theme_ids,
            extractor=extractor,
            limit=80,
        )
    else:
        insights = store.search_insights(extractor=extractor, limit=80)

    if source != "(all)":
        insights = [row for row in insights if row.get("source") == source]
    if category != "(all)":
        insights = [row for row in insights if row.get("category") == category]
    if status != "(all)":
        insights = [row for row in insights if row.get("status") == status]
    if query.strip():
        needle = query.strip().casefold()
        insights = [
            row
            for row in insights
            if needle in f"{row.get('evidence_snippet')} {row.get('text')}".casefold()
        ]
    insights = insights[:40]
    st.caption(
        f"Showing {len(insights)} quotes. The verbatim span is the evidence; interpretation is labeled separately. "
        "Packs under exports/evidence_packs/ are copies of the same quotes."
    )
    quote_cards(insights)
