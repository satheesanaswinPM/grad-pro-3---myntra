"""AI comparison agent. Reuses the discovery pipeline's LLM client (src/analyze/llm.py) -- no second
LLM client, no fabricated fallback on failure (see doc/mvp_problem_statement.md, Section 6)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analyze.llm import chat_json, llm_config
from src.mvp.state import REASON_LABELS

SYSTEM_PROMPT = (
    "You are a shopping decision assistant helping a user resolve a comparison between items they "
    "have wishlisted but not yet bought. You are not a salesperson: never mention price drops, "
    "discounts, coupons, cashback, or urgency, even though price is one of the listed attributes. "
    "Reason plainly about fit, material, occasion, and style against what the user said they are "
    "unsure about. Respond with strict JSON only, matching the schema given in the user message -- "
    "no prose outside the JSON, no markdown fences."
)

REQUIRED_TOP_KEYS = {"summary", "items", "recommendation_rationale"}


class AgentError(RuntimeError):
    """Raised when the agent cannot produce a valid comparison. Never caught to fabricate a fallback."""


def available() -> bool:
    return llm_config() is not None


def _item_block(entry: dict[str, Any]) -> str:
    product = entry["product"]
    reason = REASON_LABELS.get(entry["reason"], entry["reason"])
    fields = [
        ("id", product["id"]),
        ("title", product["title"]),
        ("brand", product["brand"]),
        ("category", product["category"]),
        ("price", product["price"]),
        ("material", product["material"]),
        ("color", product["color"]),
        ("size/fit notes", product["size_fit"]),
        ("details", product["details"]),
        ("styling/pairing notes", product["pairing"]),
        ("occasion", product["occasion"]),
        ("user's stated reason for saving it", reason),
    ]
    return "\n".join(f"{label}: {value}" for label, value in fields if value not in (None, ""))


def build_request(entries: list[dict[str, Any]]) -> dict[str, Any]:
    if len(entries) < 2:
        raise AgentError("Need at least two items to compare.")
    cfg = llm_config()
    if not cfg:
        raise AgentError("OPENAI_API_KEY is not set -- the agent has no model to call.")
    items_block = "\n\n".join(_item_block(e) for e in entries)
    schema = (
        '{"summary": "...", "items": [{"id": "<catalog id>", '
        '"fit_for_stated_reason": "...", "recommended": true|false}], '
        '"recommendation_rationale": "..."}'
    )
    user_prompt = (
        "A user is comparing these wishlisted items and hasn't decided yet:\n\n"
        f"{items_block}\n\n"
        "Compare them only on what actually differs -- fit, material, occasion fit, styling -- "
        "relative to why the user saved each one. Recommend at most one item id as the best fit for "
        "their stated reason(s); it is fine to recommend none if they are genuinely equivalent. "
        "Include every item id listed above in the \"items\" array of your response. "
        f"Respond with JSON only, matching this schema exactly: {schema}"
    )
    body: dict[str, Any] = {
        "model": cfg["model"],
        "temperature": 0.3,
        "max_completion_tokens": 900,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
    }
    if "gpt-oss" in cfg["model"]:
        body["reasoning_effort"] = "low"
    return body


def _validate(parsed: dict[str, Any], expected_ids: set[str]) -> dict[str, Any]:
    if not isinstance(parsed, dict) or not REQUIRED_TOP_KEYS.issubset(parsed.keys()):
        missing = REQUIRED_TOP_KEYS - (parsed.keys() if isinstance(parsed, dict) else set())
        raise AgentError(f"Agent response missing required keys: {sorted(missing)}")
    items = parsed.get("items")
    if not isinstance(items, list) or not items:
        raise AgentError("Agent response 'items' was empty or not a list.")
    seen_ids: set[str] = set()
    for row in items:
        if not isinstance(row, dict) or "id" not in row:
            raise AgentError("Agent response contained an item with no 'id'.")
        seen_ids.add(str(row["id"]))
    missing_ids = expected_ids - seen_ids
    if missing_ids:
        raise AgentError(f"Agent response left out items: {sorted(missing_ids)}")
    return parsed


def compare(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Call the shared LLM client and return a validated comparison. Raises AgentError on any
    failure -- callers must surface this to the UI, not fall back to a fabricated recommendation."""
    request = build_request(entries)
    expected_ids = {str(e["product"]["id"]) for e in entries}
    try:
        parsed = chat_json(request)
    except Exception as exc:  # noqa: BLE001 -- deliberately broad: any failure surfaces, none fabricate
        raise AgentError(f"Couldn't reach the assistant: {exc}") from exc
    return _validate(parsed, expected_ids)
