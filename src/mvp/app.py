"""TieBreaker -- Wishlist Comparison Agent. Streamlit UI.

Combines the two MVP mechanisms scoped for Part 5: (1) capturing *why* an item was wishlisted and
nudging the user back before attention decays, and (2) an AI agent that resolves the comparison
in-app using real product attributes. See doc/mvp_problem_statement.md for the full spec.
"""

from __future__ import annotations

import os
import random
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


# The raw scrape (data/raw/huggingface/Gssmc__myntra_dataset/train.jsonl) has no image field at
# all -- verified across every in-stock, complete row. Rather than fabricate a photo, each card
# gets an honest color swatch built from the dataset's own `dominant_color` text field.
_SWATCH_COLORS = {
    "black": "#1A1A1A", "white": "#F2F2F0", "red": "#B23A2E", "blue": "#2E5C8A",
    "green": "#3B7A4F", "yellow": "#C9A227", "pink": "#C97DA0", "purple": "#6F5A9E",
    "orange": "#C97A3D", "brown": "#6B4A34", "grey": "#8C8C8C", "gray": "#8C8C8C",
    "beige": "#D9C7A3", "maroon": "#7A2331", "navy": "#243B5C", "cream": "#E7DCC0",
    "gold": "#AD8A2E", "silver": "#B7B7B7", "multi": "#8B6FA0", "olive": "#6E7534",
    "peach": "#DDA98A", "mustard": "#C9A227", "rust": "#A5502E", "teal": "#2E7A72",
}
_SWATCH_FALLBACK = "#C9CDD6"


def _swatch_hex(color_text: str) -> str:
    t = (color_text or "").lower()
    for name, hex_value in _SWATCH_COLORS.items():
        if name in t:
            return hex_value
    return _SWATCH_FALLBACK


def _text_on(hex_value: str) -> str:
    h = hex_value.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#1A1A1A" if luminance > 0.6 else "#FFFFFF"


def _render_swatch(product: dict[str, Any]) -> None:
    bg = _swatch_hex(product.get("color", ""))
    fg = _text_on(bg)
    label = (product.get("color") or product["category"]).strip().title()
    st.markdown(
        f'<div style="width:100%;height:130px;border-radius:10px;background:{bg};'
        f'display:flex;align-items:center;justify-content:center;margin-bottom:0.6rem;">'
        f'<span style="font-size:0.68rem;font-weight:700;color:{fg};text-transform:uppercase;'
        f'letter-spacing:0.04em;text-align:center;padding:0 0.5rem;">{label}<br>'
        f'<span style="font-weight:500;opacity:0.85;">no photo in dataset</span></span></div>',
        unsafe_allow_html=True,
    )


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
                    _render_swatch(product)
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


def _render_test_result(result: dict[str, Any], entries: dict[str, dict[str, Any]]) -> None:
    st.write(result["summary"])
    for row in result["items"]:
        item_id = str(row.get("id"))
        entry = entries.get(item_id)
        title = entry["product"]["title"] if entry else item_id
        badge = " " + theme.pill("Recommended", kind="primary") if row.get("recommended") else ""
        st.markdown(f"**{title}**{badge}", unsafe_allow_html=True)
        st.write(row.get("fit_for_stated_reason", ""))
    st.caption(result["recommendation_rationale"])


def render_agent_test(items: list[dict[str, Any]]) -> None:
    st.caption(
        "Live testing pipeline for the comparison agent — fire real comparisons at it directly, "
        "outside the wishlist flow, to spot-check reasoning quality before shipping changes."
    )
    if not agent.available():
        st.warning(
            "GROQ_API_KEY is not set — the agent has no model to call. Set it in `.env` "
            "locally, or in this app's Secrets if it's deployed on Streamlit Community Cloud."
        )
        return

    cats = ["All"] + catalog.categories(items)

    st.markdown("#### Manual scenario")
    cat = st.selectbox("Category", cats, key="test_category")
    pool = items if cat == "All" else [i for i in items if i["category"] == cat]
    labels = {f"{p['title']} ({p['brand']}, {_price(p['price'])})": p for p in pool}
    picked_labels = st.multiselect("Pick 2–3 items to compare", list(labels.keys()), key="test_picks")
    reason = st.selectbox(
        "Reason (applied to every picked item)",
        list(REASON_LABELS.keys()),
        format_func=lambda r: REASON_LABELS[r],
        key="test_reason",
    )
    if st.button("Run this scenario", type="primary", disabled=len(picked_labels) < 2, key="test_run_manual"):
        entries = [{"product": labels[label], "reason": reason} for label in picked_labels]
        with st.spinner("Calling the agent..."):
            try:
                result = agent.compare(entries)
            except agent.AgentError as exc:
                st.session_state["test_last_result"] = None
                st.error(f"Agent error: {exc}")
            else:
                st.session_state["test_last_result"] = {
                    "result": result,
                    "entries": {str(e["product"]["id"]): e for e in entries},
                }
    last = st.session_state.get("test_last_result")
    if last:
        st.divider()
        _render_test_result(last["result"], last["entries"])

    st.divider()
    st.markdown("#### Batch test")
    st.caption("Run several random real comparisons back to back to spot-check consistency across items.")
    col1, col2 = st.columns(2)
    n_runs = col1.number_input("Number of comparisons", min_value=1, max_value=10, value=3, step=1, key="test_n")
    batch_cat = col2.selectbox("Category", cats, key="test_batch_category")
    if st.button("Run batch", key="test_run_batch"):
        pool2 = items if batch_cat == "All" else [i for i in items if i["category"] == batch_cat]
        results: list[dict[str, Any]] = []
        with st.spinner(f"Running {int(n_runs)} comparisons..."):
            for _ in range(int(n_runs)):
                if len(pool2) < 2:
                    break
                pair = random.sample(pool2, 2)
                entries = [{"product": p, "reason": "comparing"} for p in pair]
                try:
                    result = agent.compare(entries)
                except agent.AgentError as exc:
                    results.append({"ok": False, "entries": entries, "error": str(exc)})
                else:
                    results.append({"ok": True, "entries": entries, "result": result})
        st.session_state["test_batch_results"] = results

    batch = st.session_state.get("test_batch_results")
    if batch:
        st.markdown(f"**{sum(1 for r in batch if r['ok'])} / {len(batch)} succeeded**")
        for i, r in enumerate(batch, start=1):
            names = " vs. ".join(e["product"]["title"] for e in r["entries"])
            status = "" if r["ok"] else "  ⚠️ failed"
            with st.expander(f"{i}. {names}{status}"):
                if r["ok"]:
                    st.write(r["result"]["summary"])
                    for row in r["result"]["items"]:
                        tag = " — **recommended**" if row.get("recommended") else ""
                        st.write(f"- {row.get('id')}{tag}: {row.get('fit_for_stated_reason', '')}")
                else:
                    st.error(r["error"])


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
                "⚠️ GROQ_API_KEY is not set, so the comparison agent can't run yet. "
                "Set it in `.env` locally, or in this app's Secrets if it's deployed on "
                "Streamlit Community Cloud, to enable “Help me decide.”"
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
    st.sidebar.title("TieBreaker")
    st.sidebar.caption("Wishlist Comparison Agent · Myntra Growth")
    st.sidebar.markdown(
        "Targets the validated root cause: wishlisted comparisons go cold instead of resolving. "
        "No discounts, coupons, or price-drop framing anywhere here."
    )
    st.sidebar.divider()
    st.sidebar.markdown(f"**Simulated day: {st.session_state['sim_day']}**")
    st.sidebar.caption(
        "⏩ Fast-forward stands in for real elapsed time / push notifications, which are out of "
        "scope here -- it is a deliberate simulation, not real time."
    )
    days = st.sidebar.number_input("Days to fast-forward", min_value=1, max_value=30, value=7, step=1)
    if st.sidebar.button("⏩ Fast-forward"):
        state.fast_forward(int(days))
        st.rerun()


def _load_cloud_secrets_into_env() -> None:
    """Streamlit Community Cloud exposes configured Secrets via st.secrets, not os.environ.
    src/analyze/llm.py (shared by the pipeline and this app) only ever reads os.environ, so
    without this bridge a key set in the Cloud "Secrets" UI is invisible to it -- the app would
    keep showing "GROQ_API_KEY is not set" even after the secret is configured. Locally this is
    a no-op past what load_dotenv() already did; os.environ.setdefault never overwrites a value
    that's already set (e.g. from a real .env)."""
    try:
        secrets = st.secrets
    except Exception:
        return
    for key in ("GROQ_API_KEY", "GROQ_BASE_URL", "LLM_API_KEY", "LLM_MODEL"):
        try:
            value = secrets.get(key)
        except Exception:
            value = None
        if value:
            os.environ.setdefault(key, str(value))


def main() -> None:
    load_dotenv()
    _load_cloud_secrets_into_env()
    st.set_page_config(page_title="TieBreaker -- Wishlist Comparison Agent", layout="wide")
    theme.inject_css()
    state.init_state()
    render_sidebar()

    st.title("TieBreaker")
    st.caption(
        "The tiebreaker for your wishlist. Save real Myntra items, tell us why, and get help "
        "resolving the comparison before you forget about it. Built on a validated finding: "
        "comparisons go cold, not \"no.\""
    )

    try:
        items = _load_catalog()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    tab_browse, tab_wishlist, tab_test = st.tabs(
        ["\U0001f6cd️ Browse", "❤️ My Wishlist", "\U0001f9ea Test the Agent"]
    )
    with tab_browse:
        render_browse(items)
    with tab_wishlist:
        render_wishlist()
    with tab_test:
        render_agent_test(items)


if __name__ == "__main__":
    main()
