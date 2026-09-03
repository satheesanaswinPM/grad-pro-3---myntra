"""Shared console widgets. Quotes stay on screen; interpretation is labeled separately."""

from __future__ import annotations

from typing import Any

from src.dashboard import theme
from src.dashboard.load import Store, mix_dict, split_ids


def pct(n: int, denom: int) -> str:
    if denom <= 0:
        return "0%"
    return f"{100.0 * n / denom:.2f}%"


def status_label(status: str) -> str:
    return "`observed`" if status == "observed_evidence" else "`hypothesis`"


def banner() -> None:
    """No-op: the discovery-scope disclaimer was removed from the frontend. Kept as a function
    so every module's existing banner() call site doesn't need to change."""
    return


def quote_cards(insights: list[dict[str, Any]], empty: str = "No verbatim evidence in this slice.") -> None:
    import streamlit as st

    if not insights:
        st.caption(empty)
        return
    for item in insights:
        with st.container(border=True):
            meta = " · ".join(
                theme.meta_tag(str(v))
                for v in (
                    f"{item.get('extractor')}:{item.get('label')}",
                    item.get("source"),
                    item.get("category"),
                    item.get("journey_stage"),
                )
                if v
            )
            st.markdown(
                f"{meta} · {theme.status_pill(str(item.get('status')))} "
                f"{theme.meta_tag(str(item.get('record_id')))}",
                unsafe_allow_html=True,
            )
            st.markdown(f"> {item.get('evidence_snippet')}")
            interp = str(item.get("ai_interpretation") or "").strip()
            if interp:
                st.caption(f"INTERPRETATION (NOT THE QUOTE): {interp}")
            with st.expander("Full feedback text"):
                st.write(item.get("text") or "")


def open_evidence(record_ids: list[str], title: str, theme_ids: str = "", extractor: str = "") -> bool:
    import streamlit as st

    clicked = st.button("Read supporting feedback", key=f"ev-{title}")
    if clicked:
        st.session_state["nav"] = "Evidence explorer"
        st.session_state["evidence_ids"] = record_ids
        st.session_state["evidence_title"] = title
        st.session_state["evidence_theme_ids"] = theme_ids
        st.session_state["evidence_extractor"] = extractor
        st.rerun()
    return clicked


def opportunity_table(store: Store, rows: list[dict[str, Any]] | None = None) -> None:
    import streamlit as st

    rows = rows if rows is not None else store.opportunities
    st.dataframe(
        [
            {
                "rank": row.get("rank"),
                "opportunity": row.get("opportunity_id"),
                "total /5": row.get("total_score"),
                "freq": row.get("frequency"),
                "severity": row.get("severity"),
                "hesitation": row.get("purchase_hesitation_link"),
                "segments": row.get("segments_affected"),
                "evidence": row.get("evidence_confidence"),
                "n": row.get("unique_records"),
                "% relevant": row.get("pct_relevant"),
                "status": row.get("status"),
                "conversion link": row.get("conversion_link_status"),
            }
            for row in rows
        ],
        hide_index=True,
        width="stretch",
    )


def pick_opportunity(store: Store, key: str = "opp-pick") -> dict[str, Any] | None:
    import streamlit as st

    if not store.opportunities:
        return None
    labels = [
        f"{row.get('rank')}. {row.get('opportunity_id')}  (n={row.get('unique_records')}, {row.get('pct_relevant')}% relevant)"
        for row in store.opportunities
    ]
    choice = st.selectbox("Opportunity", labels, key=key)
    index = labels.index(choice)
    return store.opportunities[index]


def theme_table(rows: list[dict[str, Any]]) -> None:
    import streamlit as st

    st.dataframe(
        [
            {
                "theme": row.get("theme_id"),
                "n unique": row.get("unique_records"),
                "% relevant": row.get("pct_relevant"),
                "denominator": row.get("denominator_label"),
                "observed": row.get("observed_records"),
                "sources": str(mix_dict(row.get("source_mix"))),
                "status": row.get("status"),
            }
            for row in rows
        ],
        hide_index=True,
        width="stretch",
    )


def show_theme_evidence(store: Store, theme: dict[str, Any], limit: int = 12) -> None:
    import streamlit as st

    ids = split_ids(theme.get("evidence_record_ids"))
    st.caption(
        f"{theme.get('unique_records')} unique records / {theme.get('denominator')} "
        f"{theme.get('denominator_label')} ({theme.get('pct_relevant')}%). Conversion link is a hypothesis."
    )
    open_evidence(ids, str(theme.get("theme_id")), theme_ids=str(theme.get("theme_id") or ""))
    quote_cards(store.insights_for(ids, theme_ids=str(theme.get("theme_id") or ""), limit=limit))
