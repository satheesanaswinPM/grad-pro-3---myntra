"""Barrier and behavior differences by fashion category."""

from __future__ import annotations

from src.dashboard.components import banner, open_evidence, quote_cards
from src.dashboard.load import Store, split_ids


def render(store: Store) -> None:
    import streamlit as st

    st.header("Category analysis")
    banner()
    st.caption(
        "Category cuts use the relevant-in-category denominator. Rows with n_small=true are not robust. "
        "Missing extraction coverage in a category is not evidence that the barrier is absent."
    )
    st.dataframe(
        [
            {
                "category": row.get("category"),
                "barrier": row.get("theme_or_barrier"),
                "n": row.get("unique_records"),
                "% in category": row.get("pct_in_category"),
                "denominator": row.get("denominator"),
                "denominator label": row.get("denominator_label"),
                "n_small": row.get("n_small"),
                "status": row.get("status"),
            }
            for row in store.category_diffs
        ],
        hide_index=True,
        width="stretch",
    )
    if not store.category_diffs:
        return
    labels = [f"{row.get('category')} · {row.get('theme_or_barrier')}" for row in store.category_diffs]
    chosen = st.selectbox("Open category-barrier evidence", labels)
    row = store.category_diffs[labels.index(chosen)]
    if row.get("n_small"):
        st.warning("Small-n cut. Do not treat this as a robust category difference.")
    ids = split_ids(row.get("evidence_record_ids"))
    extractor = str(row.get("extractor") or "barrier")
    theme_id = f"theme:{extractor}:{row.get('theme_or_barrier')}"
    st.caption(
        f"{row.get('unique_records')} records / {row.get('denominator')} {row.get('denominator_label')} "
        f"({row.get('pct_in_category')}%)."
    )
    open_evidence(
        ids,
        f"cat-{row.get('category')}-{row.get('theme_or_barrier')}",
        theme_ids=theme_id,
        extractor=extractor,
    )
    quote_cards(
        store.insights_for(
            ids,
            extractor=extractor,
            theme_ids=theme_id,
            limit=12,
        )
    )
