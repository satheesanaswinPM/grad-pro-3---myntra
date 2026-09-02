"""Session-state wishlist model. No login, no database -- one browser session is one user (v1 scope).

Time is simulated: sim_day advances only via the explicit "fast-forward" control, standing in for
push notifications / real elapsed days, which are out of scope for this MVP.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

REASON_LABELS: dict[str, str] = {
    "comparing": "Comparing with something else",
    "occasion": "Waiting for an occasion",
    "fit": "Not sure about fit",
    "liked": "Just liked it",
}

NUDGE_THRESHOLD_DAYS = 7


def init_state() -> None:
    st.session_state.setdefault("sim_day", 0)
    st.session_state.setdefault("wishlist", {})  # item_id -> entry
    st.session_state.setdefault("decisions", [])  # log of {id, action, day}


def add_item(product: dict[str, Any], reason: str) -> None:
    st.session_state["wishlist"][product["id"]] = {
        "product": product,
        "reason": reason,
        "added_on_day": st.session_state["sim_day"],
        "last_engaged_day": st.session_state["sim_day"],
        "decision": None,
    }


def is_wishlisted(item_id: str) -> bool:
    return item_id in st.session_state["wishlist"]


def days_held(entry: dict[str, Any]) -> int:
    return st.session_state["sim_day"] - entry["added_on_day"]


def days_since_engaged(entry: dict[str, Any]) -> int:
    return st.session_state["sim_day"] - entry["last_engaged_day"]


def fast_forward(days: int) -> None:
    st.session_state["sim_day"] += days


def wishlist_items() -> dict[str, dict[str, Any]]:
    return st.session_state["wishlist"]


def comparing_items() -> dict[str, dict[str, Any]]:
    return {
        item_id: entry
        for item_id, entry in st.session_state["wishlist"].items()
        if entry["reason"] == "comparing" and entry["decision"] is None
    }


def stale_comparing_items() -> dict[str, dict[str, Any]]:
    return {
        item_id: entry
        for item_id, entry in comparing_items().items()
        if days_since_engaged(entry) >= NUDGE_THRESHOLD_DAYS
    }


def touch_engagement(item_ids: list[str]) -> None:
    """Mark items as actively re-engaged with -- resets the staleness clock without deciding them."""
    wishlist = st.session_state["wishlist"]
    for item_id in item_ids:
        if item_id in wishlist:
            wishlist[item_id]["last_engaged_day"] = st.session_state["sim_day"]


def record_decision(item_id: str, action: str) -> None:
    """action is one of: buy, keep, removed."""
    wishlist = st.session_state["wishlist"]
    if item_id not in wishlist:
        return
    st.session_state["decisions"].append(
        {"id": item_id, "action": action, "day": st.session_state["sim_day"]}
    )
    if action == "keep":
        wishlist[item_id]["last_engaged_day"] = st.session_state["sim_day"]
        return
    if action == "buy":
        wishlist[item_id]["decision"] = "buy"
        return
    wishlist.pop(item_id, None)  # removed


def resolution_tally() -> dict[str, int]:
    decisions = st.session_state["decisions"]
    resolved = sum(1 for d in decisions if d["action"] in ("buy", "removed"))
    cold = len(stale_comparing_items())
    return {"resolved": resolved, "cold": cold}
