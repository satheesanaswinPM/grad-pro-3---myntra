"""Decide -- Wishlist Comparison Agent. Streamlit UI.

Combines the two MVP mechanisms scoped for Part 5: (1) capturing *why* an item was wishlisted and
nudging the user back before attention decays, and (2) an AI agent that resolves the comparison
in-app using real product attributes. See doc/mvp_problem_statement.md for the full spec.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.ingest.env import load_dotenv
from src.mvp import agent, catalog, state, theme
from src.mvp.state import REASON_LABELS, NUDGE_THRESHOLD_DAYS


@st.cache_data(show_spinner="Loading product catalog...")
def _load_catalog() -> list[dict[str, Any]]:
    return catalog.load_catalog()


def _price(value: float) -> str:
    return f"₹{value:,.0f}"


def _truncate(text: str, n: int = 110) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def render_browse(items: list[dict[str, Any]]) -> None:
    st.caption(
        "Real Myntra product listings, filtered to a comparable demo subset "
        "(source: data/raw/huggingface/Gssmc__myntra_dataset/train.jsonl)."
    )
    cats = ["All"] + catalog.categories(items)
    chosen_cat = st.selectbox("Category", cats, key="browse_category")
    filtered = items if chosen_cat == "All" else [i for i in items if i["category"] == chosen_cat]
    st.write(f"{len(filtered)} items")

    cols_per_row = 3
    for row_start in range(0, len(filtered), cols_per_row):
        cols = st.columns(cols_per_row)
        for col, product in zip(cols, filtered[row_start : row_start + cols_per_row]):
            with col:
                with st.container(border=True):
                    st.markdown(f"**{product['title']}**")
                    st.caption(f"{product['brand']} · {product['category']} · {_price(product['price'])}")
                    if product["details"]:
                        st.write(_truncate(product["details"]))
                    if state.is_wishlisted(product["id"]):
                        st.success("In your wishlist", icon="❤️")
                    else:
                        with st.form(key=f"add_form_{product['id']}", border=False):
                            reason = st.radio(
                                "Why are you saving this?",
                                list(REASON_LABELS.keys()),
                                format_func=lambda r: REASON_LABELS[r],
                                key=f"reason_{product['id']}",
                                horizontal=False,
                            )
                            submitted = st.form_submit_button("Add to wishlist", type="primary")
                            if submitted:
                                state.add_item(product, reason)
                                st.rerun()


def _comparison_row(item_id: str, entry: dict[str, Any], *, stale: bool) -> bool:
    product = entry["product"]
    held = state.days_held(entry)
    since = state.days_since_engaged(entry)
    selected = st.checkbox(
        f"**{product['title']}** ({product['brand']}, {_price(product['price'])}) — held {held}d",
        value=True,
        key=f"select_{item_id}",
    )
    if stale:
        st.markdown(theme.pill(f"no activity for {since}d", kind="primary"), unsafe_allow_html=True)
    return selected


def _render_agent_result(result: dict[str, Any], entries: dict[str, dict[str, Any]]) -> None:
    st.markdown("#### What actually differs")
    st.write(result["summary"])
    for row in result["items"]:
        item_id = str(row.get("id"))
        entry = entries.get(item_id)
        title = entry["product"]["title"] if entry else item_id
        badge = " " + theme.pill("Recommended", kind="primary") if row.get("recommended") else ""
        st.markdown(f"**{title}**{badge}", unsafe_allow_html=True)
        st.write(row.get("fit_for_stated_reason", ""))
        if entry is not None:
            c1, c2, c3 = st.columns(3)
            if c1.button("Buy this one", key=f"buy_{item_id}", type="primary"):
                state.record_decision(item_id, "buy")
                st.session_state.pop("last_comparison", None)
                st.rerun()
            if c2.button("Keep comparing", key=f"keep_{item_id}", type="secondary"):
                state.record_decision(item_id, "keep")
                st.session_state.pop("last_comparison", None)
                st.rerun()
            if c3.button("Remove from wishlist", key=f"remove_{item_id}", type="secondary"):
                state.record_decision(item_id, "removed")
                st.session_state.pop("last_comparison", None)
                st.rerun()
    st.markdown("#### Why")
    st.write(result["recommendation_rationale"])


def render_wishlist() -> None:
    tally = state.resolution_tally()
    c1, c2, c3 = st.columns(3)
    c1.metric("Simulated day", st.session_state["sim_day"])
    c2.metric("Resolved comparisons", tally["resolved"])
    c3.metric("Still cold (no activity ≥ " + str(NUDGE_THRESHOLD_DAYS) + "d)", tally["cold"])

    wishlist = state.wishlist_items()
    if not wishlist:
        st.info("Your wishlist is empty. Add a few items under **Browse** to get started.")
        return

    stale = state.stale_comparing_items()
    if stale:
        st.warning(
            f"You've had {len(stale)} item(s) you're comparing with no activity for "
            f"{NUDGE_THRESHOLD_DAYS}+ simulated days — still deciding?",
            icon="\U0001f514",
        )

    comparing = state.comparing_items()
    if comparing:
        st.markdown("### Comparing")
        st.caption("Select 2–3 items to resolve together.")
        selected_ids = [
            item_id
            for item_id, entry in comparing.items()
            if _comparison_row(item_id, entry, stale=item_id in stale)
        ]
        if not agent.available():
            st.caption(
                "⚠️ OPENAI_API_KEY is not set, so the comparison agent can't run yet. "
                "Set it in `.env` to enable “Help me decide.”"
            )
        help_disabled = len(selected_ids) < 2 or not agent.available()
        if st.button("Help me decide", disabled=help_disabled, type="primary"):
            entries = [comparing[i] for i in selected_ids]
            try:
                result = agent.compare(entries)
            except agent.AgentError as exc:
                st.error(f"Couldn't reach the assistant — try again. ({exc})")
            else:
                state.touch_engagement(selected_ids)
                st.session_state["last_comparison"] = {
                    "result": result,
                    "entries": {i: comparing[i] for i in selected_ids},
                }
                st.rerun()

        last = st.session_state.get("last_comparison")
        if last:
            st.markdown("---")
            _render_agent_result(last["result"], last["entries"])

    others = {i: e for i, e in wishlist.items() if e["reason"] != "comparing" and e["decision"] is None}
    if others:
        st.markdown("### Other saved items")
        for item_id, entry in others.items():
            product = entry["product"]
            cols = st.columns([5, 1])
            cols[0].markdown(
                f"**{product['title']}** ({product['brand']}, {_price(product['price'])}) — "
                f"held {state.days_held(entry)}d &nbsp; {theme.pill(REASON_LABELS[entry['reason']])}",
                unsafe_allow_html=True,
            )
            if cols[1].button("Remove", key=f"remove_other_{item_id}", type="secondary"):
                state.record_decision(item_id, "removed")
                st.rerun()


def render_sidebar() -> None:
    st.sidebar.title("Decide")
    st.sidebar.caption("Wishlist Comparison Agent · Myntra Growth · Part 5 MVP")
    st.sidebar.markdown(
        "Targets the validated root cause: wishlisted comparisons go cold instead of resolving. "
        "No discounts, coupons, or price-drop framing anywhere in this MVP."
    )
    st.sidebar.divider()
    st.sidebar.markdown(f"**Simulated day: {st.session_state['sim_day']}**")
    st.sidebar.caption(
        "⏩ Fast-forward stands in for real elapsed time / push notifications, which are out of "
        "scope for this MVP -- it is a deliberate simulation, not real time."
    )
    days = st.sidebar.number_input("Days to fast-forward", min_value=1, max_value=30, value=7, step=1)
    if st.sidebar.button("⏩ Fast-forward"):
        state.fast_forward(int(days))
        st.rerun()


def main() -> None:
    load_dotenv()
    st.set_page_config(page_title="Decide -- Wishlist Comparison Agent", layout="wide")
    theme.inject_css()
    state.init_state()
    render_sidebar()

    st.title("Decide")
    st.caption(
        "Save real Myntra items, tell us why, and get help resolving the comparison before you "
        "forget about it. Built on the validated Part 4 finding: comparisons go cold, not \"no.\""
    )

    try:
        items = _load_catalog()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    tab_browse, tab_wishlist = st.tabs(["\U0001f6cd️ Browse", "❤️ My Wishlist"])
    with tab_browse:
        render_browse(items)
    with tab_wishlist:
        render_wishlist()


if __name__ == "__main__":
    main()
