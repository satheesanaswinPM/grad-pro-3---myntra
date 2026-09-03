"""Discovery → Consideration → Wishlist → Evaluation → Purchase / Abandonment."""

from __future__ import annotations

from collections import Counter

from src.dashboard.components import banner, open_evidence, pct, quote_cards
from src.dashboard.load import Store


def render(store: Store) -> None:
    import streamlit as st

    st.header("Customer journey")
    banner()
    st.caption(
        "Stages are heuristics on the relevant corpus. A review can mention purchase and still be tagged abandonment if they returned it. This is not a proven conversion funnel."
    )
    rows = []
    for stage, n in store.stage_counts():
        rows.append({"stage": stage, "n relevant": n, "% relevant": pct(n, store.n_relevant)})
    st.dataframe(rows, hide_index=True, width="stretch")

    st.subheader("Top barriers mentioned in each stage")
    st.caption("Counts are unique records in that primary stage with a barrier extraction. Denominator = relevant in stage.")
    barrier_rows = []
    for stage, n_stage in store.stage_counts():
        if n_stage <= 0:
            continue
        labels: Counter[str] = Counter()
        seen: set[tuple[str, str]] = set()
        for record_id, linked in store.relevant.items():
            if str(linked.get("journey_stage") or "") != stage:
                continue
            for item in store.by_record.get(record_id, []):
                if item["extractor"] != "barrier":
                    continue
                key = (record_id, item["label"])
                if key in seen:
                    continue
                seen.add(key)
                labels[item["label"]] += 1
        for label, n in labels.most_common(3):
            barrier_rows.append(
                {
                    "stage": stage,
                    "barrier": label,
                    "mentions": n,
                    "stage n": n_stage,
                    "% of stage": pct(n, n_stage),
                }
            )
    st.dataframe(barrier_rows, hide_index=True, width="stretch")
    st.caption("Wishlist-tagged relevant rows are few. Do not read a 4-row wishlist stage as the conversion story.")

    stages = [name for name, n in store.stage_counts() if n > 0]
    if not stages:
        return
    stage = st.selectbox("Read feedback for stage", stages)
    stage_ids = [
        record_id
        for record_id, linked in store.relevant.items()
        if str(linked.get("journey_stage") or "") == stage
        and any(item["extractor"] == "barrier" for item in store.by_record.get(record_id, []))
    ]
    st.caption(f"{len(stage_ids)} `{stage}` records with a barrier extraction.")
    open_evidence(stage_ids, f"journey:{stage}", extractor="barrier")
    quote_cards(store.insights_for(stage_ids, extractor="barrier", limit=10))
